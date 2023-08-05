import grok
import math
import transaction
from time import time
from logging import getLogger
from datetime import datetime, timedelta, date, MINYEAR
from threading import Lock, RLock

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent.wref import WeakRef

from zope import interface
from zope import component
from zope.site.hooks import getSite
from zope.annotation import IAnnotations

from grokcore import message
from z3c.taskqueue.task import SimpleTask
from hurry import query
from megrok import navigation
from plone.memoize import ram

from horae.core import service
from horae.core import utils
from horae.core import deferred
from horae.core.interfaces import IHorae, IDeferredNotifier
from horae.properties.interfaces import IComplete, IPropertied
from horae.resources.interfaces import IPlannedWorkTime, IAbsence, IPlannedResources, IPlannedResource, IWorkExpenses, IWorkExpense, IGlobalResources, IHumanResource
from horae.ticketing.interfaces import ITicketDependencies, IClient, IProject, IMilestone, ITicket, ITickets, ITicketChangedEvent
from horae.timeaware import timeaware
from horae.timeaware.interfaces import ITimeEntry, ITimeEntryContainer
from horae.layout import layout
from horae.layout.interfaces import IGlobalManageMenu, IContextualManageMenu

from horae.planning import _
from horae.planning import events
from horae.planning import interfaces

logger = getLogger('horae.planning.calculation')

THRESHOLD = 1.0 / 12
FETCH_ENTRY_DELTA = 7
MAX_ITERATIONS = 100
RETRIES = 3


class Calculator(grok.Adapter):
    """ Calculates execution of a ticket without adjustments
    """
    grok.name('simple')
    grok.implements(interfaces.ICachedCalculator)
    grok.context(interface.Interface)

    title = _(u'Forecast without adjustments')
    cssClass = 'simple'

    _key = 'horae.planning.calculation.simple'
    _global_key = 'horae.planning.calculation'
    _lock = RLock()

    def __init__(self, context):
        super(Calculator, self).__init__(context)
        self._initialize()

    def _initialize(self, clear=False):
        annotations = IAnnotations(getSite())
        if clear or not self._key in annotations:
            annotations[self._key] = PersistentDict()
        storage = annotations[self._key]
        if clear or not self._global_key in annotations:
            annotations[self._global_key] = PersistentDict()
        global_storage = annotations[self._global_key]
        if not 'invalidated' in storage:
            storage['invalidated'] = IOBTree()
        self._invalidated = storage['invalidated']
        if not 'cache' in storage:
            storage['cache'] = OOBTree()
        self._cache = storage['cache']
        if not 'cache_map' in storage:
            storage['cache_map'] = IOBTree()
        self._cache_map = storage['cache_map']
        for key in ('order', 'above', 'ticket', 'ordered', 'complete',):
            if not key in global_storage:
                global_storage[key] = IOBTree()
            setattr(self, '_' + key, global_storage[key])
        for key in ('start', 'end', 'entries',):
            if not key in storage:
                storage[key] = IOBTree()
            setattr(self, '_' + key, storage[key])
        for key in ('absence', 'possible_start', 'worktime', 'estimated_hours', 'minimum_entry_length', 'max_week_hours', 'planned_worktime',):
            setattr(self, '_' + key, IOBTree())

    @property
    @ram.cache(lambda method, inst: (method.__module__, method.__name__, getSite().__name__,))
    def query(self):
        return component.getUtility(query.query.interfaces.IQuery)

    def notify(self, ticket):
        deferred = component.getUtility(IDeferredNotifier)
        deferred.add(events.ForecastRecalculated(ticket))
        if ticket.milestone:
            deferred.add(events.ForecastRecalculated(ticket.milestone))
        deferred.add(events.ForecastRecalculated(utils.findParentByInterface(ticket, IProject)))
        deferred.add(events.ForecastRecalculated(utils.findParentByInterface(ticket, IClient)))

    def worktime(self, ticket, resource):
        """ Returns the work time for the given ticket and resource
        """
        gkey = self._group_key(ticket.id)
        if not gkey in self._worktime:
            self._worktime[gkey] = IOBTree()
        if not ticket.id in self._worktime[gkey]:
            self._worktime[gkey][ticket.id] = self.planned_worktime(ticket)
        wtime = self._worktime[gkey][ticket.id]
        if wtime is None:
            if not resource.id in self._planned_worktime:
                self._planned_worktime[resource.id] = IPlannedWorkTime(resource)
            return self._planned_worktime[resource.id]
        return wtime

    def effective(self, ticket, resource, costunit):
        """ Returns the effective worked time of the given ticket, resource and cost unit
        """
        return self.resource_costunit_map(ticket).get((resource.id, costunit.id), [])

    def absence(self, resource):
        """ Returns the absence of the given resource
        """
        if not resource.id in self._absence:
            self._absence[resource.id] = IAbsence(resource)
        return self._absence[resource.id]

    def estimated_hours(self, ticket, planned_resource):
        """ Returns the estimated hours for the planned resource
        """
        gkey = self._group_key(ticket.id)
        if not gkey in self._estimated_hours:
            self._estimated_hours[gkey] = IOBTree()
        if not ticket.id in self._estimated_hours[gkey]:
            self._estimated_hours[gkey][ticket.id] = IOBTree()
        if not planned_resource.id in self._estimated_hours[gkey][ticket.id]:
            self._estimated_hours[gkey][ticket.id][planned_resource.id] = planned_resource.hours()
        return self._estimated_hours[gkey][ticket.id][planned_resource.id]

    def fetch_entries(self, ticket):
        """ Returns whether to fetch new entries from the work time or not
        """
        return not self.complete(ticket)

    def complete(self, ticket):
        """ Returns whether this ticket is completed or not
        """
        id = ticket.id
        gkey = self._group_key(id)
        if not gkey in self._complete:
            self._complete[gkey] = IOBTree()
        if not id in self._complete[gkey]:
            self._complete[gkey][id] = IComplete(ticket, lambda: False)()
        return self._complete[gkey][id]

    def planned_resources(self, ticket):
        """ Returns the planned resources for the given ticket
        """
        return IPlannedResources(ticket).objects()

    def start(self, possible_start, start):
        """ Returns the start date
        """
        if possible_start is None and start is None:
            now = datetime.now()
            return datetime(now.year, now.month, now.day)
        if possible_start is not None:
            return start is None and possible_start or max(possible_start, start)
        return start

    def planned_worktime(self, ticket):
        """ Returns a ITimeAware holding the planned work time set on either
            the ticket, milestone or project. Returns None if no work time is
            planned
        """
        worktime = IPlannedWorkTime(ticket)
        if len(worktime.objects()):
            return worktime
        if ticket.milestone is not None:
            worktime = IPlannedWorkTime(ticket.milestone)
            if len(worktime.objects()):
                return worktime
        worktime = IPlannedWorkTime(utils.findParentByInterface(ticket, IProject))
        if len(worktime.objects()):
            return worktime
        return None

    def minimum_entry_length(self, ticket):
        """ Returns the minimum entry length for the ticket
        """
        gkey = self._group_key(ticket.id)
        if not gkey in self._minimum_entry_length:
            self._minimum_entry_length[gkey] = IOBTree()
        if not ticket.id in self._minimum_entry_length[gkey]:
            min = ticket.get_property('minimum_entry_length', None)
            if min is None:
                if ticket.milestone is not None:
                    min = ticket.milestone.get_property('minimum_entry_length', None)
            if min is None:
                project = utils.findParentByInterface(ticket, IProject)
                min = project.get_property('minimum_entry_length', None)
            if min is None:
                min = utils.findParentByInterface(project, IClient).get_property('minimum_entry_length', None)
            if min is None:
                min = THRESHOLD
            self._minimum_entry_length[gkey][ticket.id] = min
        return self._minimum_entry_length[gkey][ticket.id]

    def max_week_hours(self, ticket):
        """ Returns the maximum week hours for the ticket
        """
        gkey = self._group_key(ticket.id)
        if not gkey in self._max_week_hours:
            self._max_week_hours[gkey] = IOBTree()
        if not ticket.id in self._max_week_hours[gkey]:
            max = ticket.get_property('maximum_week_hours', None)
            if max is None:
                if ticket.milestone is not None:
                    max = ticket.milestone.get_property('maximum_week_hours', None)
            if max is None:
                max = utils.findParentByInterface(ticket, IProject).get_property('maximum_week_hours', None)
            self._max_week_hours[gkey][ticket.id] = max
        return self._max_week_hours[gkey][ticket.id]

    def possible_start(self, ticket, dependency_end=None):
        """ Returns the possible start set on either the ticket, milestone or project
            or given by a dependency. Returns None if no start date was found.
        """
        gkey = self._group_key(ticket.id)
        if not gkey in self._possible_start:
            self._possible_start[gkey] = IOBTree()
        if not ticket.id in self._possible_start[gkey]:
            start = ticket.get_property('start_due_date_start', None)
            if start is None:
                if ticket.milestone is not None:
                    start = ticket.milestone.get_property('start_due_date_start', None)
                if start is None:
                    start = utils.findParentByInterface(ticket, IProject).get_property('start_due_date_start', None)
            if ticket.get_property('dependencies', None): # check dependencies
                if dependency_end is None:
                    dependencies = ITicketDependencies(ticket).dependencies()
                    for dependency in dependencies:
                        end = self.entries(dependency, True)[2]
                        if end is not None:
                            dependency_end = dependency_end is None and end or max(dependency_end, end)
                if dependency_end is not None:
                    start = start is None and dependency_end or max(start, dependency_end)
            self._possible_start[gkey][ticket.id] = start
        return self._possible_start[gkey][ticket.id]

    def resource_costunit_map(self, ticket):
        """ Returns a dictionary keyed by resourceid, costunitid tuples holding a list
            of ITimeEntry objects representing the already registered work time for the
            ticket
        """
        map = {}
        expenses = IWorkExpenses(ticket).objects()
        for expense in expenses:
            if getattr(expense, 'timeentry', None) is None:
                continue
            key = (expense.resource.id, expense.costunit.id)
            if not key in map:
                map[key] = []
            entry = timeaware.TimeEntry()
            entry.date_start = expense.timeentry.date_start
            entry.date_end = expense.timeentry.date_end
            interface.alsoProvides(entry, interfaces.IWorkExpenseEntry)
            map[key].append(entry)
        return map

    def calculate(self, hours, start, worktime, absence=None, initial_entries=[], min_length=0.0, max_week_hours=None, fetch_entries=True):
        """ Iterator of ITimeEntry objects
        """
        possible_entries = initial_entries
        iterations = 1
        if max_week_hours is not None:
            week_hours = 0.0
            week = (MINYEAR, 1)
        while True:
            if fetch_entries:
                while not len(possible_entries) and iterations <= MAX_ITERATIONS:
                    if absence is not None:
                        possible_entries.extend(worktime.subtract(absence, (start, start + timedelta(days=FETCH_ENTRY_DELTA))).entries())
                    else:
                        possible_entries.extend(worktime.entries((start, start + timedelta(days=FETCH_ENTRY_DELTA))))
                    start += timedelta(days=FETCH_ENTRY_DELTA)
                    iterations += 1
            if not len(possible_entries):
                break
            entry = possible_entries.pop(0)
            if max_week_hours is not None:
                current_week = entry.date_start.isocalendar()[:2]
                if current_week > week:
                    week = current_week
                    week_hours = 0.0
            if not interfaces.IWorkExpenseEntry.providedBy(entry):
                if max_week_hours is not None and week_hours + entry.hours() > max_week_hours:
                    nentry = timeaware.TimeEntry()
                    nentry.date_start = entry.date_start
                    nentry.date_end = entry.date_start + timedelta(hours=max_week_hours - week_hours)
                    entry = nentry
                    if entry.hours() < min_length:
                        continue
                if entry.hours() > hours:
                    hours = math.ceil(hours * 60.0) / 60.0 # ceil to minutes
                    nentry = timeaware.TimeEntry()
                    nentry.date_start = entry.date_start
                    nentry.date_end = entry.date_start + timedelta(hours=hours)
                    entry = nentry
                    if entry.hours() < min_length:
                        break
                elif entry.hours() < min_length or entry.date_end == start + timedelta(days=FETCH_ENTRY_DELTA):
                    possible_entries.insert(0, entry)
                    if absence is not None:
                        possible_entries.extend(worktime.subtract(absence, (start, start + timedelta(days=FETCH_ENTRY_DELTA))).entries())
                    else:
                        possible_entries.extend(worktime.entries((start, start + timedelta(days=FETCH_ENTRY_DELTA))))
                    possible_entries = timeaware.flatten_entries(possible_entries)
                    if possible_entries[0].hours() < min_length:
                        possible_entries.pop(0)
                    start += timedelta(days=FETCH_ENTRY_DELTA)
                    iterations += 1
                    continue

            # adjust the hours
            hours -= entry.hours()
            if max_week_hours is not None:
                week_hours += entry.hours()

            yield entry

            if hours < min_length or iterations > MAX_ITERATIONS:
                break

    def tickets(self, resource):
        """ Iterator over the ordered tickets for a given resource
        """
        rkey = resource.id
        if not rkey in self._ordered:
            self._initialize_order(resource)
            transaction.commit()
        for id in self._ordered[rkey]:
            yield self._ticket[self._group_key(id)][id]()

    def _initialize_order(self, resource):
        s = time()
        logger.info('Initializing order for %s' % resource.name)
        rkey = resource.id
        if not rkey in self._order:
            self._order[rkey] = IOBTree()
        if not rkey in self._above:
            self._above[rkey] = IOBTree()
        if not rkey in self._ordered:
            self._ordered[rkey] = PersistentList()
        pid, prevorder = None, None
        for above in self.query.searchResults(query.And(query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                                                        query.set.AnyOf(('planning', 'plannedresources'), [rkey, ]),
                                                        query.Eq(('catalog', 'complete'), 0)), sort_field=('planning', 'position_%s' % rkey), unrestricted=True, reverse=True):
            aid = above.id
            self._ordered[rkey].append(aid)
            gkey = self._group_key(aid)
            if not gkey in self._ticket:
                self._ticket[gkey] = IOBTree()
            self._ticket[gkey][aid] = WeakRef(above)
            prevorder = [pid, ] + prevorder if pid is not None else []
            if self.possible_start(above) is not None:
                if not gkey in self._order[rkey]:
                    self._order[rkey][gkey] = IOBTree()
                self._order[rkey][gkey][aid] = prevorder
            if not gkey in self._above[rkey]:
                self._above[rkey][gkey] = IOBTree()
            self._above[rkey][gkey][aid] = pid
            pid = aid
        logger.info('Finished order initialization for %s found %s tickets in %s' % (resource.name, len(self._ordered[rkey]), time() - s))

    def _group_key(self, id):
        return id / 250

    def _clear_cache(self, id, rkey, rcukey):
        gkey = self._group_key(id)
        if not gkey in self._invalidated or not id in self._invalidated[gkey]:
            return
        if 'ticket' in self._invalidated[gkey][id]:
            for attr in ('_entries', '_start', '_end',):
                if gkey in getattr(self, attr) and id in getattr(self, attr)[gkey]:
                    del getattr(self, attr)[gkey][id]
            if gkey in self._cache_map and id in self._cache_map[gkey]:
                for method in self._cache_map[gkey][id]:
                    for key in self._cache_map[gkey][id][method]:
                        if method in self._cache and key in self._cache[method]:
                            del self._cache[method][key]
                    self._cache_map[gkey][id][method].remove(key)
                    if not len(self._cache_map[gkey][id][method]):
                        del self._cache_map[gkey][id][method]
                if not len(self._cache_map[gkey][id]):
                    del self._cache_map[gkey][id]
                if not len(self._cache_map[gkey]):
                    del self._cache_map[gkey]
            self._invalidated[gkey][id].remove('ticket')
        if rkey in self._invalidated[gkey][id]:
            self._invalidated[gkey][id].remove(rkey)
        if rcukey in self._invalidated[gkey][id]:
            self._invalidated[gkey][id].remove(rcukey)
        if not len(self._invalidated[gkey][id]):
            del self._invalidated[gkey][id]

    def _cache_key(self, obj, *args):
        if (not IClient.providedBy(obj) and
            not IProject.providedBy(obj) and
            not IMilestone.providedBy(obj)):
            return None
        return (obj.__class__.__name__, obj.id,) + tuple(args)

    def _cache_map_entry(self, gkey, id, cache_method, cache_key):
        if not gkey in self._cache_map:
            self._cache_map[gkey] = IOBTree()
        if not id in self._cache_map[gkey]:
            self._cache_map[gkey][id] = OOBTree()
        if not cache_method in self._cache_map[gkey][id]:
            self._cache_map[gkey][id][cache_method] = PersistentList()
        self._cache_map[gkey][id][cache_method].append(cache_key)

    def entries_by_planned_resource(self, obj, planned_resource, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given obj and planned_resource
        """
        entries, start, end = [], None, None
        cache_key = self._cache_key(obj, planned_resource.id)
        cache_method = 'entries_by_planned_resource'
        if not recalculate and cache_method in self._cache and cache_key in self._cache[cache_method]:
            entries, start, end = self._cache[cache_method][cache_key]
        else:
            resource = planned_resource.resource
            costunit = planned_resource.costunit
            if resource is None or costunit is None:
                aware = timeaware.TimeAware()
                aware.extend(entries)
                return aware, start, end
            rcukey = (resource.id, costunit.id)
            rkey = resource.id
            tickets = (obj,) if ITicket.providedBy(obj) else ITickets(obj)
            for ticket in tickets:
                if recalculate:
                    complete = self.complete(ticket)
                    if complete:
                        self._clear_cache(id, rkey, rcukey)
                        continue
                id = ticket.id
                gkey = self._group_key(id)
                if (recalculate and ((not gkey in self._entries or not id in self._entries[gkey] or not rcukey in self._entries[gkey][id]) or
                                     (gkey in self._invalidated and id in self._invalidated[gkey] and rcukey in self._invalidated[gkey][id]))):
                    # remove cached data before starting the recalculation
                    self._clear_cache(id, rkey, rcukey)

                    if cache_key is not None:
                        self._cache_map_entry(gkey, id, cache_method, cache_key)

                    if not gkey in self._entries:
                        self._entries[gkey] = IOBTree()
                    if not gkey in self._start:
                        self._start[gkey] = IOBTree()
                    if not gkey in self._end:
                        self._end[gkey] = IOBTree()
                    if not id in self._entries[gkey]:
                        self._entries[gkey][id] = OOBTree()
                    if not id in self._start[gkey]:
                        self._start[gkey][id] = IOBTree()
                    if not id in self._end[gkey]:
                        self._end[gkey][id] = IOBTree()
                    self._entries[gkey][id][rcukey] = PersistentList()

                    if not rkey in self._above or not gkey in self._above[rkey] or not id in self._above[rkey][gkey]:
                        self._initialize_order(resource)
                    above = self._above[rkey][gkey][id] if gkey in self._above[rkey] and id in self._above[rkey][gkey] else None
                    cstart = self._end[gkey][id][rkey] if id in self._end[gkey] and rkey in self._end[gkey][id] else None
                    if cstart is None and above is not None:
                        cend = self.entries_by_resource(self._ticket[self._group_key(above)][above](), resource, recalculate)[2]
                        if cend is not None:
                            cstart = cstart is None and cend or max(cend, cstart)
                    s = time()
                    possible_start = self.possible_start(ticket)
                    worktime = self.worktime(ticket, resource)
                    estimated_hours = self.estimated_hours(ticket, planned_resource)
                    min_length = self.minimum_entry_length(ticket)
                    max_week_hours = self.max_week_hours(ticket)
                    fetch_entries = self.fetch_entries(ticket)
                    absence = self.absence(resource)
                    cstart = self.start(possible_start, cstart)

                    initial_entries = []

                    astart = cstart
                    if not complete:
                        # if we have a possible start date find gaps between the start and possible start date
                        if possible_start is not None and possible_start < cstart:
                            wtime = worktime
                            if absence is not None:
                                wtime = worktime.subtract(absence, (possible_start, cstart))
                            order = self._order[rkey][gkey][id] if gkey in self._order[rkey] and id in self._order[rkey][gkey] else []
                            for aid in order:
                                wtime = wtime.subtract(self._entries[self._group_key(aid)][aid].get(rkey, timeaware.TimeAware()), (possible_start, cstart))
                            initial_entries.extend(wtime.entries())

                        if absence is not None:
                            initial_entries.extend(worktime.subtract(absence, (cstart, cstart + timedelta(days=FETCH_ENTRY_DELTA))).entries())
                        else:
                            initial_entries.extend(worktime.entries((cstart, cstart + timedelta(days=FETCH_ENTRY_DELTA))))
                        initial_entries = timeaware.flatten_entries(initial_entries)
                        cstart = cstart + timedelta(days=FETCH_ENTRY_DELTA)

                    # the first possible entries are the ones of the work expenses
                    effective = self.effective(ticket, resource, costunit)
                    initial_entries = effective + initial_entries

                    entry = None
                    for entry in self.calculate(estimated_hours, cstart, worktime, absence, initial_entries, min_length, max_week_hours, fetch_entries):
                        self._start[gkey][id][rkey] = entry.date_start if not rkey in self._start[gkey][id] else min(entry.date_start, self._start[gkey][id][rkey])
                        self._end[gkey][id][rkey] = entry.date_end if not rkey in self._end[gkey][id] else max(entry.date_end, self._end[gkey][id][rkey])
                        if not isinstance(entry, timeaware.PersistentTimeEntry):
                            nentry = timeaware.PersistentTimeEntry()
                            nentry.date_start = entry.date_start
                            nentry.date_end = entry.date_end
                            entry = nentry
                        self._entries[gkey][id][rcukey].append(entry)

                    if not rkey in self._end[gkey][id] or self._end[gkey][id][rkey] is None:
                        self._end[gkey][id][rkey] = astart
                    if not rkey in self._start[gkey][id] or self._start[gkey][id][rkey] is None:
                        self._start[gkey][id][rkey] = astart

                    self.notify(ticket)
                    transaction.commit()
                    logger.info('Recalculated %s #%s (%s, %s) %s' % (self.cssClass, id, resource.name, costunit.name, time() - s))

                start = self._start[gkey][id].get(rkey, None) if gkey in self._start and id in self._start[gkey] else None
                end = self._end[gkey][id].get(rkey, None) if gkey in self._end and id in self._end[gkey] else None
                if gkey in self._entries and id in self._entries[gkey]:
                    entries.extend(self._entries[gkey][id].get(rcukey, []))

            if cache_key is not None:
                if not cache_method in self._cache:
                    self._cache[cache_method] = OOBTree()
                self._cache[cache_method][cache_key] = (entries, start, end,)

        aware = timeaware.TimeAware()
        aware.extend(entries)

        return aware, start, end

    def entries_by_resource(self, obj, resource, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given object and resource
        """
        entries, start, end = [], None, None
        cache_key = self._cache_key(obj, resource.id)
        cache_method = 'entries_by_resource'
        if not recalculate and cache_method in self._cache and cache_key in self._cache[cache_method]:
            entries, start, end = self._cache[cache_method][cache_key]
        else:
            tickets = (obj,) if ITicket.providedBy(obj) else ITickets(obj)
            for ticket in tickets:
                if cache_key is not None:
                    gkey = self._group_key(ticket.id)
                    self._cache_map_entry(gkey, ticket.id, cache_method, cache_key)
                rid = resource.id
                for planned_resource in self.planned_resources(ticket):
                    if not planned_resource.resource_id == rid:
                        continue
                    e, st, en = self.entries_by_planned_resource(ticket, planned_resource, recalculate)
                    entries.extend(e.objects())
                    if st is not None:
                        start = st if start is None else min(start, st)
                    if en is not None:
                        end = en if end is None else max(end, en)
            if cache_key is not None:
                if not cache_method in self._cache:
                    self._cache[cache_method] = OOBTree()
                self._cache[cache_method][cache_key] = (entries, start, end,)

        aware = timeaware.TimeAware()
        aware.extend(entries)
        return aware, start, end

    def entries(self, obj, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given object
        """
        cache_key = self._cache_key(obj)
        cache_method = 'entries'
        if not recalculate and cache_method in self._cache and cache_key in self._cache[cache_method]:
            entries, start, end = self._cache[cache_method][cache_key]
        else:
            entries, start, end = [], None, None
            tickets = (obj,) if ITicket.providedBy(obj) else ITickets(obj)
            for ticket in tickets:
                if cache_key is not None:
                    gkey = self._group_key(ticket.id)
                    self._cache_map_entry(gkey, ticket.id, cache_method, cache_key)
                for planned_resource in self.planned_resources(ticket):
                    e, st, en = self.entries_by_planned_resource(ticket, planned_resource, recalculate)
                    entries.extend(e.objects())
                    if st is not None:
                        start = st if start is None else min(start, st)
                    if en is not None:
                        end = en if end is None else max(end, en)
            if cache_key is not None:
                if not cache_method in self._cache:
                    self._cache[cache_method] = OOBTree()
                self._cache[cache_method][cache_key] = (entries, start, end,)

        aware = timeaware.TimeAware()
        aware.extend(entries)
        return aware, start, end

    def available(self, ticket, planned_resource):
        """ Whether this calculation is available for the given ticket and planned_resource
        """
        return True

    def calculated(self):
        """ Returns the date of the last calculation
        """
        annotations = IAnnotations(getSite())
        return annotations[self._key]['calculated'] if 'calculated' in annotations[self._key] else None

    def mark_calculation(self):
        """ Sets the calculation date to today
        """
        annotations = IAnnotations(getSite())
        annotations[self._key]['calculated'] = date.today()

    def invalidate_all(self, clear_cache=True):
        """ Invalidates all cached calculations
        """
        for gkey in self._entries.keys():
            self._invalidated[gkey] = IOBTree()
            for id in self._entries[gkey].keys():
                self._invalidated[gkey][id] = PersistentList()
                self._invalidated[gkey][id].append('ticket')
                if clear_cache:
                    for attr in ('_possible_start', '_worktime', '_estimated_hours', '_minimum_entry_length', '_max_week_hours', '_complete',):
                        if id in getattr(self, attr):
                            del getattr(self, attr)[gkey][id]
                for rkey, cukey in self._entries[gkey][id].keys():
                    if not rkey in self._invalidated[gkey][id]:
                        self._invalidated[gkey][id].append(rkey)
                    if not (cukey, rkey) in self._invalidated[gkey][id]:
                        self._invalidated[gkey][id].append((rkey, cukey))
                    if clear_cache:
                        for attr in ('_order', '_absence', '_above', '_planned_worktime', '_ordered',):
                            if rkey in getattr(self, attr):
                                del getattr(self, attr)[rkey]

    def invalidate(self, obj, invalidate_below=True):
        """ Invalidates the cache for the given object
        """
        invalidate = []
        tickets = (obj,) if ITicket.providedBy(obj) else ITickets(obj)
        for ticket in tickets:
            if ticket in invalidate:
                invalidate.remove(ticket)
            id = ticket.id
            gkey = self._group_key(id)
            complete = self.complete(ticket)
            if not gkey in self._invalidated:
                self._invalidated[gkey] = IOBTree()
            self._invalidated[gkey][id] = PersistentList()
            self._invalidated[gkey][id].append('ticket')
            for attr in ('_possible_start', '_worktime', '_estimated_hours', '_minimum_entry_length', '_max_week_hours', '_complete',):
                if id in getattr(self, attr):
                    del getattr(self, attr)[gkey][id]
            for planned_resource in self.planned_resources(ticket):
                resource = planned_resource.resource
                rkey = planned_resource.resource_id
                cukey = planned_resource.costunit_id
                self._invalidated[gkey][id].append(rkey)
                self._invalidated[gkey][id].append((rkey, cukey))
                if complete:
                    self._clear_cache(id, rkey, (rkey, cukey))
                for attr in ('_order', '_absence', '_above', '_planned_worktime', '_ordered',):
                    if rkey in getattr(self, attr):
                        del getattr(self, attr)[rkey]
                if invalidate_below and resource is not None:
                    queries = [query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                               query.set.AnyOf(('planning', 'plannedresources'), [rkey, ]),
                               query.Le(('planning', 'position_%s' % rkey), component.getMultiAdapter((ticket, planned_resource.resource), interfaces.IPositionedObject).position - 1)]
                    for below in self.query.searchResults(query.And(*queries), unrestricted=True):
                        if not below in invalidate:
                            invalidate.append(below)
            for dependent in ITicketDependencies(ticket).dependents():
                if not dependent in invalidate:
                    invalidate.append(dependent)
        for below in invalidate:
            self.invalidate(below, False)

    def clear_cache(self, method=None):
        """ Clear the cache of the calculator, optionally only for a given method
        """
        if method is None:
            annotations = IAnnotations(getSite())
            storage = annotations[self._key]
            storage['cache'] = OOBTree()
            self._cache = storage['cache']
            storage['cache_map'] = IOBTree()
            self._cache_map = storage['cache_map']
        else:
            self._cache[method] = OOBTree()
        transaction.commit()


class NoMaxWeekHoursCalculator(Calculator):
    """ Calculates execution of a ticket with no maximum week hours
    """
    grok.name('no_max_week_hours')

    title = _(u'Forecast with no maximum week hours')
    cssClass = 'no_max_week_hours'

    _key = 'horae.planning.calculation.no_max_week_hours'
    _lock = RLock()

    def notify(self, ticket):
        pass

    def max_week_hours(self, ticket):
        """ Override of the default method returning always None
        """
        return None

    def available(self, ticket, planned_resource):
        """ Whether this calculation is available for the given ticket and planned_resource
        """
        return super(NoMaxWeekHoursCalculator, self).max_week_hours(ticket) is not None


class NoAbsenceCalculator(Calculator):
    """ Calculates execution of a ticket ignoring all absences
    """
    grok.name('no_absence')

    title = _(u'Forecast ignoring all absences')
    cssClass = 'no_absence'

    _key = 'horae.planning.calculation.no_absence'
    _lock = RLock()

    def notify(self, ticket):
        pass

    def absence(self, resource):
        """ Override of the default method returning always None
        """
        return None

    def available(self, ticket, planned_resource):
        """ Whether this calculation is available for the given ticket and planned_resource
        """
        absence = super(NoAbsenceCalculator, self).absence(planned_resource.resource)
        return absence is not None and len(absence.objects()) > 0


class NoAbsenceAndMaxWeekHoursCalculator(NoAbsenceCalculator):
    """ Calculates execution of a ticket ignoring all absences and the maximum week hours
    """
    grok.name('no_absence_and_max_week_hours')

    title = _(u'Forecast ignoring all absences and the maximum week hours')
    cssClass = 'no_absence_and_max_week_hours'

    _key = 'horae.planning.calculation.no_absence_and_max_week_hours'
    _lock = RLock()

    def max_week_hours(self, ticket):
        """ Override of the default method returning always None
        """
        return None

    def available(self, ticket, planned_resource):
        """ Whether this calculation is available for the given ticket and planned_resource
        """
        return super(NoAbsenceAndMaxWeekHoursCalculator, self).available(ticket, planned_resource) and \
               super(NoAbsenceAndMaxWeekHoursCalculator, self).max_week_hours(ticket) is not None


class DeferredInvalidator(deferred.BaseQueue, grok.GlobalUtility):
    """ Utility handling deferred calculation invalidation
    """
    grok.implements(interfaces.IDeferredInvalidator)

    index_factory = IOBTree

    _queue_attr = '__horae_planning_invalidatequeue'
    _index_attr = '__horae_planning_invalidateindex'
    _calculators = None

    def _key(self, obj):
        return obj.id

    @property
    def calculators(self):
        #try:
        if self._calculators is None:
            self._calculators = [(name, calculator) for name, calculator in component.getAdapters((getSite(),), interfaces.ICachedCalculator)]
        return self._calculators
        #except:
        #    return []

    def action(self, obj):
        for name, calculator in self.calculators:
            calculator.invalidate(obj)


@grok.subscribe(interfaces.IPositionableObject, interfaces.IPositionChangedEvent)
@grok.subscribe(ITimeEntry, grok.IObjectRemovedEvent)
@grok.subscribe(ITimeEntry, grok.IObjectAddedEvent)
@grok.subscribe(ITimeEntry, grok.IObjectModifiedEvent)
@grok.subscribe(IPropertied, grok.IObjectModifiedEvent)
@grok.subscribe(IPlannedResource, grok.IObjectRemovedEvent)
@grok.subscribe(IPlannedResource, grok.IObjectAddedEvent)
@grok.subscribe(IPlannedResource, grok.IObjectModifiedEvent)
@grok.subscribe(IWorkExpense, grok.IObjectAddedEvent)
@grok.subscribe(IWorkExpense, grok.IObjectRemovedEvent)
def invalidate_calculations(obj, event):
    """ Invalidates calculations of an object
    """
    if IPropertied.providedBy(obj) and grok.IContainerModifiedEvent.providedBy(event):
        return
    if IPropertied.providedBy(obj) and not interfaces.IPositionChangedEvent.providedBy(event) and not ITicketChangedEvent.providedBy(event):
        properties = [name for name, value in obj.current().properties()]
        if not 'start_due_date_start' in properties and \
           not 'start_due_date_end' in properties and \
           not 'estimated_hours' in properties and \
           not 'dependencies' in properties and \
           not 'minimum_entry_length' in properties and \
           not 'maximum_week_hours' in properties and \
           not 'workflow' in properties:
            return
    parent = obj
    if grok.IObjectAddedEvent.providedBy(event):
        parent = event.newParent
    if grok.IObjectRemovedEvent.providedBy(event):
        parent = event.oldParent
    if ITimeEntry.providedBy(obj):
        if grok.IObjectModifiedEvent.providedBy(event):
            parent = utils.findParentByInterface(obj, ITimeEntryContainer)
        if (not IPlannedWorkTime.providedBy(parent) and
            not IAbsence.providedBy(parent)):
            return
    parent = utils.findParentByInterface(parent, ITicket)
    if parent is None:
        parent = utils.findParentByInterface(obj, IMilestone)
    if parent is None:
        parent = utils.findParentByInterface(obj, IProject)
    if parent is None:
        parent = utils.findParentByInterface(obj, IClient)
    if parent is not None:
        invalidator = component.getUtility(interfaces.IDeferredInvalidator)
        for ticket in ITickets(parent):
            invalidator.add(ticket)
    else:
        for name, calculator in component.getAdapters((obj,), interfaces.ICachedCalculator):
            calculator.invalidate_all()

recalculation_lock = Lock()
recalculation_map = {}


def _recalculate(site, calculator, q):
    for resource in IGlobalResources(site).objects():
        if not IHumanResource.providedBy(resource):
            continue
        for ticket in calculator.tickets(resource):
            calculator.entries_by_resource(ticket, resource, True)


def recalculate_site_forecasts(site):
    if recalculation_map.get(site.__name__, False):
        return False
    recalculation_map[site.__name__] = True
    logger.info('Starting forecast recalculation in site %s' % site.__name__)
    retries = 0
    q = component.getUtility(query.query.interfaces.IQuery)
    notifier = component.getUtility(IDeferredNotifier)
    calculators = [(name, calculator) for name, calculator in component.getAdapters((site,), interfaces.ICalculator)]
    while True:
        try:
            for name, calculator in calculators:
                start = time()
                logger.info('Starting recalculation of %s forecasts in site %s' % (name, site.__name__))
                try:
                    if calculator.calculated() is None or calculator.calculated() < date.today():
                        calculator.invalidate_all(False)
                        calculator.mark_calculation()
                    _recalculate(site, calculator, q)
                except Exception:
                    logger.info('Recalculation of invalidated failed, starting recalculation of all tickets')
                    calculator._initialize(True)
                    _recalculate(site, calculator, q)
                calculator.clear_cache('entries')
                notifier()
                transaction.commit()
                logger.info('Recalculated %s forecasts in site %s (%s)' % (name, site.__name__, time() - start))
            transaction.commit()
            logger.info('Finished forecast recalculation in site %s' % site.__name__)
            break
        except Exception:
            transaction.abort()
            if retries > 3:
                logger.error('Forecast recalculation failed in site %s' % site.__name__, exc_info=True)
                break
            retries += 1
            logger.warning('Retrying forecast recalculation in site %s' % site.__name__, exc_info=True)
    recalculation_map[site.__name__] = False


def recalculate_forecasts(*args):
    recalculation_lock.acquire()
    for site in service.sites():
        try:
            recalculate_site_forecasts(site)
        except:
            pass
    recalculation_lock.release()

grok.global_utility(SimpleTask(recalculate_forecasts), name=u'horae.planning.calculation.recalculate_forecasts', direct=True)


@grok.subscribe(service.IHoraeServiceInitialized)
def add_task(event):
    event.service.addCronJob(u'horae.planning.calculation.recalculate_forecasts', minute=(10, 30, 50))


class RecalculateForecasts(layout.View):
    """ View to recalculate all forecasts
    """
    grok.context(IHorae)
    grok.require('horae.Plan')
    grok.name('recalculate-forecasts')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Recalculate forecasts'))

    def __call__(self):
        if recalculate_site_forecasts(self.context) is False:
            message.send(_(u'Forecasts calculation already started'), u'info', u'session')
        else:
            message.send(_(u'Forecasts successfully recalculated'), u'info', u'session')
        self.redirect(self.request.get('HTTP_REFERER', self.url(self.context)))

    def render(self):
        return ''


class ContextualRecalculateForecasts(layout.View):
    """ Base view to recalculate the forecasts in a given context
    """
    grok.baseclass()
    grok.require('horae.Plan')
    grok.name('recalculate-forecasts')
    navigation.menuitem(IContextualManageMenu, _(u'Recalculate forecasts'))

    def __call__(self):
        calculators = [(name, calculator) for name, calculator in component.getAdapters((self.context,), interfaces.ICalculator)]
        for ticket in ITickets(self.context):
            for name, calculator in calculators:
                if calculator.calculated() is None or calculator.calculated() < date.today():
                    calculator.invalidate_all(False)
                    calculator.mark_calculation()
                calculator.entries(ticket, True)
        self.redirect(self.request.get('HTTP_REFERER', self.url(self.context)))
        message.send(_(u'Forecasts successfully recalculated'), u'info', u'session')

    def render(self):
        return ''


class ClientRecalculateForecasts(ContextualRecalculateForecasts):
    """ View to recalculate the forecasts of a client
    """
    grok.context(IClient)


class ProjectRecalculateForecasts(ContextualRecalculateForecasts):
    """ View to recalculate the forecasts of a project
    """
    grok.context(IProject)


class MilestoneRecalculateForecasts(ContextualRecalculateForecasts):
    """ View to recalculate the forecasts of a milestone
    """
    grok.context(IMilestone)


class TicketRecalculateForecasts(ContextualRecalculateForecasts):
    """ View to recalculate the forecasts of a ticket
    """
    grok.context(ITicket)
