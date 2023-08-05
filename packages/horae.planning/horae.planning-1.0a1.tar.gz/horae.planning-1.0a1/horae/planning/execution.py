import grok
import operator
from time import time
from logging import getLogger
from datetime import datetime, MINYEAR
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent.wref import WeakRef
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree

from grokcore import message

from zope import component
from zope import interface
from zope.annotation import IAnnotations

from hurry import query

from megrok import navigation

from horae.core import utils
from horae.core.interfaces import IHorae, IDeferredNotifier
from horae.search.utils import normalizeDatetime
from horae.layout import layout
from horae.layout.interfaces import IGlobalManageMenu, IContextualManageMenu
from horae.timeaware import timeaware
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket, ITickets
from horae.resources.interfaces import IGlobalResources, IHumanResource, ICostUnit, ICostUnits

from horae.planning import _
from horae.planning import events
from horae.planning import interfaces

logger = getLogger('horae.planning.execution')


class EstimatedExecutionOfObject(timeaware.TimeAware):
    """ Information about estimated execution of an object
    """
    grok.implements(interfaces.IEstimatedExecutionOfObject)

    _flatten = False

    def __init__(self, context):
        super(EstimatedExecutionOfObject, self).__init__(context)
        self.storage = {}

    def _wrapped(self, method, ticket, milestone, project, client, *args, **kwargs):
        if self._ticket is None:
            self._ticket = ticket
        if self._milestone is None:
            self._milestone = milestone
        if self._project is None:
            self._project = project
        if self._client is None:
            self._client = client
        result = getattr(super(EstimatedExecutionOfObject, self), method)(*args, **kwargs)
        if self._ticket == ticket:
            self._ticket = None
        if self._milestone == milestone:
            self._milestone = None
        if self._project == project:
            self._project = None
        if self._client == client:
            self._client = None
        return result

    def _get_ids(self, ticket=None, milestone=None, project=None, client=None):
        ids = []
        if ticket is not None:
            if isinstance(ticket, list):
                for id in ticket:
                    ids.extend(self.storage['by_ticket'].get(id, []))
                return ids
            return self.storage['by_ticket'].get(ticket, [])
        elif milestone is not None:
            if isinstance(milestone, list):
                for id in milestone:
                    ids.extend(self.storage['by_milestone'].get(id, []))
                return ids
            return self.storage['by_milestone'].get(milestone, [])
        elif project is not None:
            if isinstance(project, list):
                for id in project:
                    ids.extend(self.storage['by_project'].get(id, []))
                return ids
            return self.storage['by_project'].get(project, [])
        elif client is not None:
            if isinstance(client, list):
                for id in client:
                    ids.extend(self.storage['by_client'].get(id, []))
                return ids
            return self.storage['by_client'].get(client, [])
        return None

    def initialize(self, storage):
        self.storage = storage

    def hours(self, daterange=None, ticket=None, project=None, milestone=None, client=None):
        """ Returns the sum of the hours of the contained time entries,
            optionally only for a given ticket, milestone, project or client
        """
        return self._wrapped('hours', ticket, milestone, project, client, daterange)

    def start(self, ticket=None, milestone=None, project=None, client=None):
        """ Returns the estimated start date and time,
            optionally only for a given ticket, milestone, project or client
        """
        ids = self._get_ids(ticket, milestone, project, client)
        start = None
        if ids is not None:
            for id in ids:
                cstart = self.storage['start'].get(id, None)
                if cstart is not None:
                    start = start is None and cstart or min(cstart, start)
        else:
            for cstart in self.storage['start'].values():
                start = start is None and cstart or min(cstart, start)
        return start

    def end(self, ticket=None, milestone=None, project=None, client=None):
        """ Returns the estimated end date and time,
            optionally only for a given ticket, milestone, project or client
        """
        ids = self._get_ids(ticket, milestone, project, client)
        end = None
        if ids is not None:
            for id in ids:
                cend = self.storage['end'].get(id, None)
                if cend is not None:
                    end = end is None and cend or max(cend, end)
        else:
            for cend in self.storage['end'].values():
                end = end is None and cend or max(cend, end)
        return end

    def objects(self, daterange=None, ticket=None, milestone=None, project=None, client=None):
        """ Returns a list of all contained time entries,
            optionally only for a given ticket, milestone, project or client
        """
        return self._wrapped('objects', ticket, milestone, project, client, daterange)

    def entries(self, daterange=None, ticket=None, milestone=None, project=None, client=None):
        """ Returns a list of non repeating time entries to cover the provided date range,
            optionally only for a given ticket, milestone, project or client
        """
        return self._wrapped('entries', ticket, milestone, project, client, daterange)

    def get_entries(self):
        ids = self._get_ids(self._ticket, self._milestone, self._project, self._client)
        if ids is None:
            entries = []
            for ref in self.storage['entries'].values():
                entry = ref()
                if entry is not None:
                    entries.append(entry)
        else:
            entries = []
            for id in ids:
                ref = self.storage['entries'].get(id, None)
                if ref is None:
                    continue
                entry = ref()
                if entry is not None:
                    entries.append(entry)
        entries.sort(key=operator.attrgetter('date_start'))
        return entries

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)


class CachedEstimatedExecutionOfObject(grok.Adapter, EstimatedExecutionOfObject):
    """ Cached information about estimated execution of an object
    """
    grok.baseclass()
    grok.context(IHumanResource)
    grok.provides(interfaces.ICachedEstimatedExecutionOfObject)

    _key = 'horae.planning.estimatedexecution'
    _ticket = None
    _milestone = None
    _project = None
    _client = None

    def __init__(self, context):
        super(CachedEstimatedExecutionOfObject, self).__init__(context)
        storage = IAnnotations(context)
        if not self._key in storage:
            self._initialize_storage()
        self.storage = storage[self._key]

    def _initialize_storage(self):
        storage = IAnnotations(self.context)
        storage[self._key] = PersistentDict()
        storage[self._key]['by_ticket'] = IOBTree()
        storage[self._key]['by_milestone'] = IOBTree()
        storage[self._key]['by_project'] = IOBTree()
        storage[self._key]['by_client'] = IOBTree()
        storage[self._key]['entries'] = IOBTree()
        storage[self._key]['start'] = IOBTree()
        storage[self._key]['end'] = IOBTree()
        storage[self._key]['intid'] = 1
        self.storage = storage[self._key]

    def initialize(self, storage):
        return # not allowed

    def _remove(self, ids):
        for id in ids:
            ref = self.storage['entries'].get(id, None)
            if ref is None:
                continue
            entry = ref()
            if entry is None:
                continue
            by_ticket = self.storage['by_ticket'].get(entry.ticket, [])
            if id in by_ticket:
                by_ticket.remove(id)
            if entry.milestone is not None:
                by_milestone = self.storage['by_milestone'].get(entry.ticket, [])
                if id in by_milestone:
                    by_milestone.remove(id)
            by_project = self.storage['by_project'].get(entry.ticket, [])
            if id in by_project:
                by_project.remove(id)
            by_client = self.storage['by_client'].get(entry.ticket, [])
            if id in by_client:
                by_client.remove(id)
            del self.storage['entries'][id]
            del self.storage['start'][id]
            del self.storage['end'][id]

    def remove(self, ticket=None, milestone=None, project=None, client=None):
        """ Removes the stored entries for a given ticket, milestone, project or client
        """
        ids = self._get_ids(ticket, milestone, project, client)
        if ids is None:
            self._initialize_storage()
            return
        self._remove(ids)

    def extend(self, timeentries):
        """ Extends the object by the provided list of IEstimationTimeEntry objects
        """
        for entry in timeentries:
            self.append(entry)

    def append(self, timeentry):
        """ Extends the object by the provided list of IEstimationTimeEntry objects
        """
        if not interfaces.IEstimationTimeEntry.providedBy(timeentry):
            raise ValueError('Entry has to implement IEstimationTimeEntry')
        i = self.storage['intid']
        self.storage['entries'][i] = WeakRef(timeentry)
        self.storage['start'][i] = timeentry.date_start
        self.storage['end'][i] = timeentry.date_end
        if not timeentry.ticket in self.storage['by_ticket']:
            self.storage['by_ticket'][timeentry.ticket] = PersistentList()
        self.storage['by_ticket'][timeentry.ticket].append(i)
        if timeentry.milestone is not None:
            if not timeentry.milestone in self.storage['by_milestone']:
                self.storage['by_milestone'][timeentry.milestone] = PersistentList()
            self.storage['by_milestone'][timeentry.milestone].append(i)
        if not timeentry.project in self.storage['by_project']:
            self.storage['by_project'][timeentry.project] = PersistentList()
        self.storage['by_project'][timeentry.project].append(i)
        if not timeentry.client in self.storage['by_client']:
            self.storage['by_client'][timeentry.client] = PersistentList()
        self.storage['by_client'][timeentry.client].append(i)
        self.storage['intid'] += 1

    def history_entry(self, date=None):
        """ Creates a new entry in the history optionally for a given date
        """
        if not len(self.storage['entries']):
            return
        if not 'history' in self.storage:
            self.storage['history'] = IOBTree()
        if date is None:
            date = datetime.now()
        key = normalizeDatetime(datetime(date.year, date.month, date.day, date.hour, date.minute))
        if key in self.storage['history']:
            return
        if not 'dates' in self.storage:
            self.storage['dates'] = IOBTree()
        entry = PersistentDict()
        for tree in ('by_ticket', 'by_milestone', 'by_project', 'by_client'):
            entry[tree] = IOBTree()
            for k, v in self.storage[tree].items():
                entry[tree][k] = PersistentList()
                entry[tree][k].extend(v[:])
        entry['entries'] = IOBTree()
        for k, ref in self.storage['entries'].items():
            obj = ref()
            if obj is not None:
                entry['entries'][k] = WeakRef(obj)
        entry['start'] = IOBTree()
        for k, start in self.storage['start'].items():
            entry['start'][k] = start
        entry['end'] = IOBTree()
        for k, end in self.storage['end'].items():
            entry['end'][k] = end
        self.storage['dates'][key] = date
        self.storage['history'][key] = entry

    def history_before(self, date):
        """ Returns an IEstimatedExecutionOfObject containing the information of the last history entry before the given date
            or None if no entry was found
        """
        for c in self.history_dates():
            if c > date:
                continue
            entry = EstimatedExecutionOfObject()
            entry.initialize(self.storage['history'][normalizeDatetime(c)])
            return entry
        return None

    def history_dates(self, hidden=False):
        """ Returns a list of dates of the available history entries
        """
        if not 'dates' in self.storage:
            return []
        dates = reversed(sorted(self.storage['dates'].values()))
        if not hidden and 'hidden' in self.storage:
            return [date for date in dates if not date in self.storage['hidden']]
        return dates

    def hide_history_entry(self, date):
        """ Marks a specific history entry as hidden
        """
        if not 'hidden' in self.storage:
            self.storage['hidden'] = PersistentList()
        if not date in self.storage['hidden']:
            self.storage['hidden'].append(date)

    def show_history_entries(self):
        """ Marks all history entries as visible
        """
        if 'hidden' in self.storage:
            del self.storage['hidden']

    def clear_history(self):
        """ Clears the history
        """
        if 'dates' in self.storage:
            del self.storage['dates']
        if 'history' in self.storage:
            del self.storage['history']


class CachedEstimatedExecutionOfHumanResource(CachedEstimatedExecutionOfObject):
    """ Estimated execution of a human resource
    """
    grok.context(IHumanResource)


class CachedEstimatedExecutionOfCostUnit(CachedEstimatedExecutionOfObject):
    """ Estimated execution of a cost unit
    """
    grok.context(ICostUnit)


class EstimatedExecution(grok.Adapter, timeaware.TimeAware):
    """ Cached information about the estimated execution of a given object
    """
    grok.baseclass()
    grok.implements(interfaces.IEstimatedExecution)

    _human_resource = None
    _costunit = None
    _flatten = False

    def _wrapped(self, method, human_resource, costunit, *args, **kwargs):
        if self._human_resource is None:
            self._human_resource = human_resource
        if self._costunit is None:
            self._costunit = costunit
        result = getattr(super(EstimatedExecution, self), method)(*args, **kwargs)
        if self._human_resource == human_resource:
            self._human_resource = None
        if self._costunit == costunit:
            self._costunit = None
        return result

    def hours(self, daterange=None, human_resource=None, costunit=None, default=None):
        """ Returns the sum of the hours of the contained time entries, optionally only for a given human resource
        """
        return self._wrapped('hours', human_resource, costunit, daterange)

    def start(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated start date and time, optionally only for a given human resource
        """
        raise NotImplementedError(u'concrete classes must implement start()')

    def end(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated end date and time, optionally only for a given human resource
        """
        raise NotImplementedError(u'concrete classes must implement end()')

    def objects(self, daterange=None, human_resource=None, costunit=None):
        """ Returns a list of all contained time entries, optionally only for a given human resource
            or cost unit
        """
        return self._wrapped('objects', human_resource, costunit, daterange)

    def entries(self, daterange=None, human_resource=None, costunit=None):
        """ Returns a list of non repeating time entries to cover the provided date range,
            optionally only for a given human resource or cost unit
        """
        return self._wrapped('entries', human_resource, costunit, daterange)

    def calculated(self):
        """ The date and time of the calculation
        """
        raise NotImplementedError(u'concrete classes must implement calculated()')

    def user(self):
        """ The user who issued the calculation or None
        """
        return None

    def message(self):
        """ The optional message added to the calculation
        """
        return None

    def due_date(self):
        """ Returns the due date set on either the ticket, milestone or project.
            Returns None if no due date was found.
        """
        return None


class TicketEstimatedExecution(EstimatedExecution):
    """ Information about the estimated execution of a given object
    """
    grok.baseclass()

    storage = {}

    def initialize(self, storage):
        self.storage = storage

    def hours(self, daterange=None, human_resource=None, costunit=None, default=None):
        """ Returns the sum of the hours of the contained time entries, optionally only for a given human resource
            or cost unit
        """
        if daterange is None:
            hours = 0.0
            if human_resource is not None and costunit is not None:
                return self.storage['hours']['by_resource_costunit'].get((human_resource, costunit), default)
            if human_resource is not None:
                if isinstance(human_resource, list):
                    for id in human_resource:
                        hours += self.storage['hours']['by_resource'].get(id, 0.0)
                    return hours
                return self.storage['hours']['by_resource'].get(human_resource, default)
            if costunit is not None:
                if isinstance(costunit, list):
                    for id in costunit:
                        hours += self.storage['hours']['by_resource'].get(id, 0.0)
                    return hours
                return self.storage['hours']['by_costunit'].get(costunit, default)
            return self.storage['hours'].get(0, default)
        return super(TicketEstimatedExecution, self).hours(daterange, human_resource, costunit, default)

    def start(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated start date and time, optionally only for a given human resource
            or cost unit
        """
        if human_resource is not None and costunit is not None:
            return self.storage['start']['by_resource_costunit'].get((human_resource, costunit), default)
        start = None
        if human_resource is not None:
            if isinstance(human_resource, list):
                for id in human_resource:
                    s = self.storage['start']['by_resource'].get(id, None)
                    if s is not None:
                        start = s if start is None else min(start, s)
                return start if start is not None else default
            return self.storage['start']['by_resource'].get(human_resource, default)
        if costunit is not None:
            if isinstance(costunit, list):
                for id in costunit:
                    s = self.storage['start']['by_costunit'].get(id, None)
                    if s is not None:
                        start = s if start is None else min(start, s)
                return start if start is not None else default
            return self.storage['start']['by_costunit'].get(costunit, default)
        return self.storage['start'].get(0, default)

    def end(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated end date and time, optionally only for a given human resource
            or cost unit
        """
        if human_resource is not None and costunit is not None:
            return self.storage['start']['by_resource_costunit'].get((human_resource, costunit), default)
        end = None
        if human_resource is not None:
            if isinstance(human_resource, list):
                for id in human_resource:
                    e = self.storage['end']['by_resource'].get(id, None)
                    if e is not None:
                        end = e if end is None else max(end, e)
                return end if end is not None else default
            return self.storage['end']['by_resource'].get(human_resource, default)
        if costunit is not None:
            if isinstance(costunit, list):
                for id in costunit:
                    e = self.storage['end']['by_costunit'].get(id, None)
                    if e is not None:
                        end = e if end is None else max(end, e)
                return end if end is not None else default
            return self.storage['end']['by_costunit'].get(costunit, default)
        return self.storage['end'].get(0, default)

    def calculated(self):
        """ The date and time of the last calculation
        """
        return self.storage.get('calculated', datetime(MINYEAR, 1, 1))

    def user(self):
        """ The user who issued the calculation or None
        """
        return self.storage.get('user', None)

    def message(self):
        """ The optional message added to the calculation
        """
        return self.storage.get('message', None)

    def due_date(self):
        """ Returns the due date set on either the ticket, milestone or project.
            Returns None if no due date was found.
        """
        due = self.context.get_property('start_due_date_end', None)
        if due is None:
            if self.milestone is not None:
                due = self.milestone.get_property('start_due_date_end', None)
            if due is None:
                due = self.project.get_property('start_due_date_end', None)
        return due

    def get_entries(self):
        ids = []
        if self._human_resource is not None and self._costunit is not None:
            ids = self.storage['by_resource_costunit'].get((self._human_resource, self._costunit), [])
        elif self._human_resource is not None:
            if isinstance(self._human_resource, list):
                for id in self._human_resource:
                    ids.extend(self.storage['by_resource'].get(id, []))
            else:
                ids = self.storage['by_resource'].get(self._human_resource, [])
        elif self._costunit is not None:
            if isinstance(self._costunit, list):
                for id in self._costunit:
                    ids.extend(self.storage['by_costunit'].get(id, []))
            else:
                ids = self.storage['by_costunit'].get(self._costunit, [])
        else:
            ids = self.storage['entries'].keys()
        for id in ids:
            entry = self.storage['entries'].get(id, None)
            if entry is not None:
                yield entry

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)


class CachedTicketEstimatedExecution(TicketEstimatedExecution):
    """ Cached information about the estimated execution of a given object
    """
    grok.context(ITicket)
    grok.provides(interfaces.ICachedEstimatedExecution)

    _cache_key = 'horae.planning.estimatedexecutioncache'
    cache = {}

    def __init__(self, context):
        super(EstimatedExecution, self).__init__(context)
        storage = IAnnotations(context)
        if not self._cache_key in storage:
            storage[self._cache_key] = PersistentDict()
            self.storage = storage[self._cache_key]
            self._initialize_storage()
        self.storage = storage[self._cache_key]
        self.milestone = self.context.milestone
        self.project = utils.findParentByInterface(self.context, IProject)
        self.client = utils.findParentByInterface(self.project, IClient)

    def _initialize_storage(self):
        self.storage['start'] = PersistentDict()
        self.storage['start']['by_resource'] = IOBTree()
        self.storage['start']['by_costunit'] = IOBTree()
        self.storage['start']['by_resource_costunit'] = OOBTree()
        self.storage['end'] = PersistentDict()
        self.storage['end']['by_resource'] = IOBTree()
        self.storage['end']['by_costunit'] = IOBTree()
        self.storage['end']['by_resource_costunit'] = OOBTree()
        self.storage['hours'] = PersistentDict()
        self.storage['hours']['by_resource'] = IOBTree()
        self.storage['hours']['by_costunit'] = IOBTree()
        self.storage['hours']['by_resource_costunit'] = OOBTree()
        self.storage['entries'] = IOBTree()
        self.storage['by_resource'] = IOBTree()
        self.storage['by_costunit'] = IOBTree()
        self.storage['by_resource_costunit'] = OOBTree()

    def recalculate(self, user=None, message=None):
        """ Recalculates the different entries and dates optionally marked by a username and annotated with a message
        """
        start = time()
        self.history_entry()
        self._initialize_storage()
        self._calculate_entries()
        self.storage['calculated'] = datetime.now()
        self.storage['user'] = user
        self.storage['message'] = message
        logger.info('Recalculated ticket #%s (%s)' % (self.context.id, time() - start))

    def history_entry(self):
        """ Creates a new entry in the history
        """
        calculated = self.calculated()
        if calculated != datetime(MINYEAR, 1, 1):
            if not 'history' in self.storage:
                self.storage['history'] = IOBTree()
            if not 'dates' in self.storage:
                self.storage['dates'] = IOBTree()
            history = PersistentDict()
            history['start'] = self.storage['start']
            history['end'] = self.storage['end']
            history['hours'] = self.storage['hours']
            history['entries'] = self.storage['entries']
            history['by_resource'] = self.storage['by_resource']
            history['by_costunit'] = self.storage['by_costunit']
            history['by_resource_costunit'] = self.storage['by_resource_costunit']
            history['calculated'] = calculated
            history['user'] = self.storage.get('user', None)
            history['message'] = self.storage.get('message', None)
            self.storage['dates'][normalizeDatetime(calculated)] = calculated
            self.storage['history'][normalizeDatetime(calculated)] = history

    def history_before(self, date):
        """ Returns an IEstimatedExecution containing the information of the last history entry before the given date
            or None if no entry was found
        """
        for c in self.history_dates():
            if c > date:
                continue
            entry = TicketEstimatedExecution(self.context)
            entry.initialize(self.storage['history'][normalizeDatetime(c)])
            return entry
        return None

    def history_dates(self, hidden=False):
        """ Returns a list of dates of the available history entries
        """
        if not 'dates' in self.storage:
            return []
        dates = reversed(sorted(self.storage['dates'].values()))
        if not hidden and 'hidden' in self.storage:
            return [date for date in dates if not date in self.storage['hidden']]
        return dates

    def hide_history_entry(self, date):
        """ Marks a specific history entry as hidden
        """
        if not 'hidden' in self.storage:
            self.storage['hidden'] = PersistentList()
        if not date in self.storage['hidden']:
            self.storage['hidden'].append(date)

    def show_history_entries(self):
        """ Marks all history entries as visible
        """
        if 'hidden' in self.storage:
            del self.storage['hidden']

    def clear_history(self):
        """ Clears the history
        """
        if 'dates' in self.storage:
            del self.storage['dates']
        if 'history' in self.storage:
            del self.storage['history']

    def _calculate_entries(self):
        ticket_start = None
        ticket_end = None
        ticket_hours = 0.0
        id = self.context.id
        mid = None
        if self.milestone is not None:
            mid = self.milestone.id
        pid = self.project.id
        cid = self.client.id
        i = 1
        calculator = component.getAdapter(self.context, interfaces.ICalculator, 'simple')
        for planned_resource in calculator.planned_resources(self.context):
            resource = planned_resource.resource
            costunit = planned_resource.costunit
            resource_execution = interfaces.IEstimatedExecutionOfObject(resource)
            costunit_execution = interfaces.IEstimatedExecutionOfObject(costunit)
            rkey, cukey = resource.id, costunit.id
            rcukey = (rkey, cukey)
            entries, start, end = calculator.entries_by_planned_resource(self.context, planned_resource, True)
            for entry in entries.objects():
                # initialize the different caches and maps
                if not rcukey in self.storage['by_resource_costunit']:
                    self.storage['by_resource_costunit'][rcukey] = PersistentList()
                    self.storage['hours']['by_resource_costunit'][rcukey] = entry.hours()
                else:
                    self.storage['hours']['by_resource_costunit'][rcukey] += entry.hours()
                if not rkey in self.storage['by_resource']:
                    self.storage['by_resource'][rkey] = PersistentList()
                    self.storage['hours']['by_resource'][rkey] = entry.hours()
                else:
                    self.storage['hours']['by_resource'][rkey] += entry.hours()
                if not cukey in self.storage['by_costunit']:
                    self.storage['by_costunit'][cukey] = PersistentList()
                    self.storage['hours']['by_costunit'][cukey] = entry.hours()
                else:
                    self.storage['hours']['by_costunit'][cukey] += entry.hours()

                # let the entry implement IEstimationTimeEntry
                entry.resourcecostunit = WeakRef(planned_resource)
                entry.ticket = id
                entry.milestone = mid
                entry.project = pid
                entry.client = cid
                interface.alsoProvides(entry, interfaces.IEstimationTimeEntry)

                # add the entry to the different caches
                self.storage['entries'][i] = entry
                self.storage['by_resource'][rkey].append(i)
                self.storage['by_costunit'][cukey].append(i)
                self.storage['by_resource_costunit'][rcukey].append(i)

                # add the entry to the resources and costunits execution storage
                resource_execution.append(entry)
                costunit_execution.append(entry)

                # update the variables for the ticket
                ticket_start = ticket_start is None and entry.date_start or min(entry.date_start, ticket_start)
                ticket_end = ticket_end is None and entry.date_end or max(entry.date_end, ticket_end)
                ticket_hours += entry.hours()
                i += 1

            self.storage['start']['by_resource_costunit'][rcukey] = start
            self.storage['end']['by_resource_costunit'][rcukey] = end
            self.storage['start']['by_costunit'][cukey] = start
            self.storage['end']['by_costunit'][cukey] = end
            self.storage['start']['by_resource'][rkey] = start
            self.storage['end']['by_resource'][rkey] = end

        # add the overall start and end date and hours
        self.storage['start'][0] = ticket_start
        self.storage['end'][0] = ticket_end
        self.storage['hours'][0] = ticket_hours

        # reindex the related objects
        deferred = component.getUtility(IDeferredNotifier)
        deferred.add(events.EstimatedExecutionRecalculated(self.context))
        if self.milestone is not None:
            deferred.add(events.EstimatedExecutionRecalculated(self.milestone))
        deferred.add(events.EstimatedExecutionRecalculated(self.project))
        deferred.add(events.EstimatedExecutionRecalculated(self.client))


class ContainerEstimatedExecution(EstimatedExecution):
    """ Base class for estimated execution of containers
    """
    grok.baseclass()

    key = 'horae.planning.estimatedexecution'

    def tickets(self):
        return ITickets(self.context)

    def clear_cache(self):
        storage = IAnnotations(self.context)
        storage[self.key] = OOBTree()

    @property
    def cache(self):
        storage = IAnnotations(self.context)
        if not self.key in storage:
            storage[self.key] = OOBTree()
        return storage[self.key]

    def _initialize_cache(self, human_resource=None, costunit=None):
        cache = self.cache
        key = (human_resource, costunit)
        if not key in cache:
            hours = 0.0
            start = None
            end = None
            calculated = None
            for ticket in self.tickets():
                execution = interfaces.IEstimatedExecution(ticket)
                hours += execution.hours(None, human_resource, costunit, 0.0)

                tstart = execution.start(human_resource, costunit)
                if tstart is None:
                    continue
                start = start is None and tstart or min(start, tstart)

                tend = execution.end(human_resource, costunit)
                if tend is None:
                    continue
                end = end is None and tend or max(end, tend)

                tcalculated = execution.calculated()
                if tcalculated is None:
                    continue
                calculated = calculated is None and tcalculated or max(calculated, tcalculated)

            cache[key] = OOBTree()
            cache['calculated'] = calculated
            cache[key]['hours'] = hours
            cache[key]['start'] = start
            cache[key]['end'] = end

    def hours(self, daterange=None, human_resource=None, costunit=None, default=None):
        """ Returns the sum of the hours of the contained time entries, optionally only for a given human resource
            or cost unit
        """
        if daterange is None:
            self._initialize_cache(human_resource, costunit)
            return self.cache[(human_resource, costunit)]['hours']
        else:
            hours = 0.0
            for ticket in self.tickets():
                hours += interfaces.IEstimatedExecution(ticket).hours(daterange, human_resource, costunit, 0.0)
            return hours

    def start(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated start date and time, optionally only for a given human resource
            or cost unit
        """
        self._initialize_cache(human_resource, costunit)
        return self.cache[(human_resource, costunit)]['start']

    def end(self, human_resource=None, costunit=None, default=None):
        """ Returns the estimated end date and time, optionally only for a given human resource
            or cost unit
        """
        self._initialize_cache(human_resource, costunit)
        return self.cache[(human_resource, costunit)]['end']

    def calculated(self):
        """ The date and time of the last calculation
        """
        self._initialize_cache()
        calculated = self.cache['calculated']
        return calculated is not None and calculated or datetime(MINYEAR, 1, 1)

    def get_entries(self):
        entries = []
        for ticket in self.tickets():
            entries.extend(interfaces.IEstimatedExecution(ticket).objects(self._human_resource, self._costunit))
        return entries

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)


class MilestoneEstimatedExecution(ContainerEstimatedExecution):
    """ Estimated execution of a ticket
    """
    grok.context(IMilestone)
    grok.provides(interfaces.IEstimatedExecution)

    def due_date(self):
        """ Returns the due date set on either the ticket, milestone or project.
            Returns None if no due date was found.
        """
        due = self.context.get_property('start_due_date_end', None)
        if due is None:
            due = utils.findParentByInterface(self.context, IProject).get_property('start_due_date_end', None)
        return due


class ProjectEstimatedExecution(ContainerEstimatedExecution):
    """ Estimated execution of a project
    """
    grok.context(IProject)
    grok.provides(interfaces.IEstimatedExecution)

    def due_date(self):
        """ Returns the due date set on either the ticket, milestone or project.
            Returns None if no due date was found.
        """
        return self.context.get_property('start_due_date_end', None)


class ClientEstimatedExecution(ContainerEstimatedExecution):
    """ Estimated execution of a client
    """
    grok.context(IClient)
    grok.provides(interfaces.IEstimatedExecution)


@grok.subscribe(IClient, interfaces.IEstimatedExecutionRecalculated)
@grok.subscribe(IProject, interfaces.IEstimatedExecutionRecalculated)
@grok.subscribe(IMilestone, interfaces.IEstimatedExecutionRecalculated)
def clear_execution_cache(obj, event):
    """ Clears the cache of the estimated execution adapter after
        recalculation
    """
    interfaces.IEstimatedExecution(obj).clear_cache()


class ClearTicketPlanningHistory(layout.DeleteForm):
    """ View to clear the planning history of a ticket
    """
    grok.context(ITicket)
    grok.require('horae.Manage')
    grok.name('clear-ticket-estimation-history')
    navigation.menuitem(IContextualManageMenu, _(u'Clear planning history'))

    def clear(self):
        interfaces.IEstimatedExecution(self.context).clear_history()

    @property
    def label(self):
        return _(u'Delete planning history of ${ticket}', mapping={'ticket': self.context.get_property('name')})

    def item_title(self):
        return _(u'the planning history of ${ticket}', mapping={'ticket': self.context.get_property('name')})

    def next_url(self):
        return self.url(self.context)

    @property
    def msg(self):
        return _(u'The planning history of ${ticket} successfully deleted', mapping={'ticket': self.context.get_property('name')})

    def delete(self):
        self.clear()


class RecalculateEstimations(layout.Form):
    """ View to recalculate the estimated executions of all tickets
        based on the current forecast
    """
    grok.context(IHorae)
    grok.require('horae.Plan')
    grok.name('recalculate-estimations')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Recalculate estimated execution'))

    form_fields = grok.AutoFields(interfaces.IRecalculationForm)
    label = _(u'Recalculate estimated execution')

    def recalculate(self, user, message):
        try:
            results = component.getUtility(query.interfaces.IQuery).searchResults(query.query.And(query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                                                                                                  query.query.Eq(('catalog', 'complete'), 0)), unrestricted=True)
        except TypeError:
            return
        # create a cache entry for all resources and remove all cached entries
        date = datetime.now()
        for resource in IGlobalResources(self.context).objects():
            if not IHumanResource.providedBy(resource):
                continue
            exc = interfaces.ICachedEstimatedExecutionOfObject(resource)
            exc.history_entry(date)
            exc.remove()
        # create a cache entry for all cost units and remove all cached entries
        for costunit in ICostUnits(self.context).objects():
            exc = interfaces.ICachedEstimatedExecutionOfObject(costunit)
            exc.history_entry(date)
            exc.remove()
        # recalculate the given ticket
        for ticket in results:
            interfaces.IEstimatedExecution(ticket).recalculate(user, message)

    @grok.action(_(u'Recalculate'))
    def handle_recalculate(self, **data):
        self.recalculate(self.request.principal.id, data['message'])
        message.send(_(u'Estimated execution successfully recalculated'), u'info', u'session')
        self.redirect(self.url(self.context))


class ClearPlanningHistory(layout.DeleteForm):
    """ View to clear the planning history of all tickets
    """
    grok.context(IHorae)
    grok.require('horae.Manage')
    grok.name('clear-estimation-history')
    navigation.menuitem(IGlobalManageMenu, _(u'Clear planning history'))

    def clear(self):
        try:
            results = component.getUtility(query.interfaces.IQuery).searchResults(query.query.And(query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ])), unrestricted=True)
        except TypeError:
            return
        for ticket in results:
            interfaces.IEstimatedExecution(ticket).clear_history()

    @property
    def label(self):
        return _(u'Delete planning history of all tickets')

    def item_title(self):
        return _(u'the planning history of all tickets')

    @property
    def msg(self):
        return _(u'The planning history of all tickets successfully deleted')

    def next_url(self):
        return self.url(self.context)

    def delete(self):
        self.clear()
