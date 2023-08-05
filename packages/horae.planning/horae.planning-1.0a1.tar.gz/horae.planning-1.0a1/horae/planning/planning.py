# -*- coding: utf-8 -*-
import grok
import json
from hashlib import sha1

from zope import component
from zope.interface import classImplements
from zope.i18n import translate
from zope.site.hooks import getSite
from zope.location.interfaces import ILocationInfo
from zope.catalog.interfaces import ICatalog
from zope.annotation import IAnnotations
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IRequest
from zope.event import notify
from zope.intid.interfaces import IIntIds

from plone.memoize import ram

from hurry.query.interfaces import IQuery
from hurry.query import set, query

from megrok import navigation

from horae.core.utils import findParentByInterface
from horae.core.interfaces import IHorae
from horae.layout.interfaces import IDisplayView, IActionsMenu, IViewsMenu, IMainActionsMenu, IObjectTableActionsProvider
from horae.search.search import row_factory_cache_key
from horae.search.interfaces import ISortingProvider
from horae.search.utils import normalizeDatetime
from horae.ticketing.utils import getObjectType
from horae.ticketing import ticketing
from horae.ticketing import user
from horae.ticketing import _ as _t
from horae.ticketing.interfaces import IProject, ITicket, ITicketDependencies
from horae.resources.interfaces import IGlobalResourcesHolder, IGlobalResources, IHumanResource

from horae.planning import _
from horae.planning import interfaces
from horae.planning import events
from horae.planning.extenders import render_execution

grok.templatedir('templates')

classImplements(ticketing.Project, interfaces.IPositionableObject)
classImplements(ticketing.Ticket, interfaces.IPositionableObject)


class ResourceTraverser(grok.MultiAdapter):
    """ Namespace traverser for resources
    """
    grok.adapts(IHorae, IRequest)
    grok.name('resource')
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return IGlobalResources(self.context).get_object(name)


class Index(user.Index):
    """ Base view of human resource rendering a table of tickets the resource
        is planned for
    """
    grok.implements(IDisplayView)
    grok.context(IHumanResource)
    grok.require('horae.View')
    grok.template('resource')
    grok.baseclass()
    no_results_msg = _(u'The selected resource is currently not planned for any ticket.')
    page_size = None

    @ram.cache(row_factory_cache_key)
    def row_factory(self, object, columns, request):
        row = super(Index, self).row_factory(object, columns, request)
        if IHumanResource.providedBy(self.context):
            row['execution'] = render_execution(object, request, self.context.id)
        return row

    @property
    def caption(self):
        return _(u'Open tickets planned for ${name}', mapping={'name': self.context.name})

    def query(self):
        return query.And(set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                         set.AnyOf(('planning', 'plannedresources'), [self.context.id, ]),
                         query.Eq(('catalog', 'complete'), 0))

    def base_url(self):
        return self.url(getSite()) + '/++resource++' + str(self.context.id)

    def session_key(self):
        return sha1(self.base_url()).hexdigest()


class ResourceIndex(Index):
    """ View of human resource rendering a table of tickets the resource
        is planned for
    """
    grok.name('index')
    navigation.menuitem(IViewsMenu, _t(u'Tickets'))


class ResourcesTicketActionProvider(grok.Adapter):
    """ Action provider for human resources adding an action to the
        list of tickets the resource is planned for
    """
    grok.context(IHumanResource)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.planning.resources.tickets')

    order = 1

    def actions(self, request):
        return [{'url': '%s/++resource++%s' % (grok.url(request, findParentByInterface(self.context, IHorae)), self.context.id),
                 'label': translate(_t(u'Tickets'), context=request),
                 'cssClass': 'button-alternative'}, ]


class PositionedObject(grok.Adapter):
    """ A positioned object
    """
    grok.context(interfaces.IPositionableObject)
    grok.implements(interfaces.IPositionedObject)

    _key = 'horae.planning.position'

    def __init__(self, context):
        self.context = context
        self.storage = IAnnotations(context, None)
        if self.storage is not None:
            if not self._key in self.storage:
                self.storage[self._key] = None

    def get_position(self):
        if self.storage[self._key] is not None:
            return self.storage[self._key]
        id = -self.context.id
        parent = findParentByInterface(self.context, interfaces.IPositionableObject, 1)
        if parent is not None:
            id += 10 ** 10 * interfaces.IPositionedObject(parent).position
        return id

    def set_position(self, value):
        self.storage[self._key] = value
        notify(events.PositionChangedEvent(self.context))
    position = property(get_position, set_position)


class PositionedObjectByResource(grok.MultiAdapter):
    """ A positioned object by resource
    """
    grok.adapts(interfaces.IPositionableObject, IHumanResource)
    grok.implements(interfaces.IPositionedObject)

    def __init__(self, context, resource):
        self.context = context
        self.resource = resource
        self.storage = IAnnotations(context, None)
        if self.storage is not None:
            if not self._key in self.storage:
                self.storage[self._key] = None

    @property
    def _key(self):
        return 'horae.planning.position.%s' % self.resource.id

    def get_position(self):
        if self.storage[self._key] is not None:
            return self.storage[self._key]
        return interfaces.IPositionedObject(self.context).position

    def set_position(self, value):
        self.storage[self._key] = value
        notify(events.PositionChangedEvent(self.context))
    position = property(get_position, set_position)


@grok.subscribe(interfaces.IPositionableObject, interfaces.IPositionChangedEvent)
def reindex_object_position(obj, event):
    """ Reindexes the position index after a position has changed
    """
    catalog = component.getUtility(ICatalog, 'catalog')
    planning = component.getUtility(ICatalog, 'planning')
    intid = component.getUtility(IIntIds, context=catalog)
    results = component.getUtility(IQuery).searchResults(set.AnyOf(('catalog', 'path'), [ILocationInfo(obj).getPath(), ]))
    sorting = catalog['sorting']
    indexes = [planning['position'], ]
    for resource in IGlobalResources(findParentByInterface(obj, IGlobalResourcesHolder)).objects():
        if IHumanResource.providedBy(resource):
            indexes.append(planning['position_%s' % resource.id])
    for ob in results:
        sorting.index_doc(intid.queryId(ob), ob)
        for index in indexes:
            index.index_doc(intid.queryId(ob), ob)


@grok.subscribe(ITicket, grok.IObjectModifiedEvent)
def check_dependencies(obj, event):
    """ Checks and moves a ticket according to its dependencies after
        it has been modified
    """
    deps = obj.get_property('dependencies')
    if not deps:
        return
    pos = interfaces.IPositionedObject(obj)
    map = {}
    map[pos.position] = None
    dependencies = ITicketDependencies(obj)
    for dep in dependencies.dependencies():
        map[interfaces.IPositionedObject(dep).position] = dep
    swap = min(map.keys())
    if map[swap] is None: # already at lowest position
        return
    move_object_below(ITicket, obj, swap)
    check_dependencies(map[swap], event)
    for dependent in dependencies.dependents(): # check objects depending on me
        check_dependencies(dependent, event)


@grok.subscribe(IProject, grok.IObjectModifiedEvent)
def check_date(obj, event):
    """ Checks and moves a project according to its start date after
        it has been modified
    """
    start = obj.get_property('start_due_date_start', None)
    pos = interfaces.IPositionedObject(obj)
    if start is not None: # move project after projects having a lower end date
        results = component.getUtility(IQuery).searchResults(query.And(set.AnyOf(('catalog', 'implements'), [IProject.__identifier__, ]),
                                                                       query.Le(('properties', 'start_due_date_end'), normalizeDatetime(start)),
                                                                       query.Eq(('catalog', 'complete'), 0)),
                                                                       query.Le(('planning', 'position'), pos.position), sort_field=('planning', 'position'), limit=1)
        if len(results):
            for result in results:
                move_object_below(IProject, obj, interfaces.IPositionedObject(result).position)
                break
    end = obj.get_property('start_due_date_end', None)
    if end is not None: # move project before projects having a higher start date
        results = component.getUtility(IQuery).searchResults(query.And(set.AnyOf(('catalog', 'implements'), [IProject.__identifier__, ]),
                                                                       query.Ge(('properties', 'start_due_date_start'), normalizeDatetime(end)),
                                                                       query.Eq(('catalog', 'complete'), 0)),
                                                                       query.Ge(('planning', 'position'), pos.position), sort_field=('planning', 'position'), reverse=True, limit=1)
        if len(results):
            for result in results:
                move_object_above(IProject, obj, interfaces.IPositionedObject(result).position)
                break


def swap_objects(one, two, resource=None):
    if resource is None:
        pos_one = interfaces.IPositionedObject(one)
        pos_two = interfaces.IPositionedObject(two)
    else:
        pos_one = component.getMultiAdapter((one, resource), interfaces.IPositionedObject)
        pos_two = component.getMultiAdapter((two, resource), interfaces.IPositionedObject)
    pos_one.position, pos_two.position = pos_two.position, pos_one.position


def object_range(interface, min, max, reverse=False, resource=None):
    index = 'position' if resource is None else 'position_%s' % resource.id
    q = query.And(set.AnyOf(('catalog', 'implements'), [interface.__identifier__, ]),
                  query.Between(('planning', index), min, max))
    return component.getUtility(IQuery).searchResults(q, sort_field=('planning', index), reverse=reverse)


def move_object_above(interface, obj, position, resource=None):
    pos = interfaces.IPositionedObject(obj).position if resource is None else component.getMultiAdapter((obj, resource), interfaces.IPositionedObject).position
    affected = object_range(interface, pos + 1, position, resource=resource)
    for o in affected:
        swap_objects(o, obj, resource)


def move_object_below(interface, obj, position, resource=None):
    pos = interfaces.IPositionedObject(obj).position if resource is None else component.getMultiAdapter((obj, resource), interfaces.IPositionedObject).position
    affected = object_range(interface, position, pos - 1, True, resource=resource)
    for o in affected:
        swap_objects(o, obj, resource)


class PositionSortingProvider(grok.Adapter):
    """ Sorting provider for positionable objects returning
        the position itself
    """
    grok.context(interfaces.IPositionableObject)
    grok.implements(ISortingProvider)

    def add(self):
        """ Returns an integer to be added to the sorting
        """
        return interfaces.IPositionedObject(self.context).position

    def adjust(self, sorting):
        """ Adjusts the sorting after all providers sorting where added and returns the adjusted sorting
        """
        return sorting


class PlanResourceTickets(Index):
    """ View providing the functionality to reorder the tickets of
        a resource and thus changing their priority
    """
    grok.require('horae.Plan')
    grok.name('plan')
    grok.implements(interfaces.IPlanningView)
    navigation.menuitem(IActionsMenu, _(u'Plan tickets'))
    navigation.menuitem(IMainActionsMenu, _(u'Plan tickets'))

    _calculator = None

    @property
    def calculator(self):
        if self._calculator is None:
            self._calculator = component.getAdapter(self.context, interfaces.ICalculator, 'simple')
        return self._calculator

    @property
    def resource(self):
        return self.context

    def row_factory(self, object, columns, request):
        link = self._chain[object.id]
        row = super(PlanResourceTickets, self).row_factory(object, columns, request)
        row['sort'] = u''
        if link['prev'] is not None:
            row['sort'] += u'<a class="button button-discreet" href="%s?moveup=%s" title="%s">▲</a> ' % (self.base_url(), object.id, translate(_(u'Move up'), context=request))
        if link['next'] is not None:
            row['sort'] += u'<a class="button button-discreet" href="%s?movedn=%s" title="%s">▼</a> ' % (self.base_url(), object.id, translate(_(u'Move down'), context=request))
        if row['sort']:
            row['sort'] = u'<div class="button-group">%s</div>' % row['sort']
        start, end = self.calculator.entries(object)[1:] if self.resource is None else self.calculator.entries_by_resource(object, self.resource)[1:]
        row['forecast'] = render_execution(object, request, start=start, end=end)
        due_date = interfaces.IEstimatedExecution(object).due_date() if ITicket.providedBy(object) else object.get_property('start_due_date_end')
        row['due_date'] = object.find_property('start_due_date').render(due_date, self.context, self.request)
        return row

    @property
    def caption(self):
        return _(u'Plan open tickets for ${name}', mapping={'name': self.context.name})

    def base_url(self):
        return self.url(getSite()) + '/++resource++' + str(self.context.id) + '/@@plan'

    def createTable(self):
        table = super(PlanResourceTickets, self).createTable()
        table.css_class = 'plan'
        table.sortable = None
        table.filterable = None
        table.columns = [column for column in table.columns if not column[0] is 'modification_date']
        table.columns.insert(0, ('sort', ''))
        table.columns.insert(-2, ('due_date', _(u'Due date')))
        table.columns.append(('forecast', _(u'Forecast')))
        return table

    def results(self):
        results, table = super(PlanResourceTickets, self).results()
        self._chain = {}
        new_results = []
        prev = None
        try:
            moveup = int(self.request.form.get('moveup'))
        except:
            moveup = None
        try:
            movedn = int(self.request.form.get('movedn'))
        except:
            movedn = None
        for ticket in results:
            dependencies = ITicketDependencies(ticket)
            new_results.append(ticket)
            link = dict(element=ticket, next=None, prev=None)
            self._chain[ticket.id] = link
            if prev is not None:
                allowed = True
                for dep in dependencies.dependencies(False):
                    if prev['element'].id == dep:
                        allowed = False
                        break
                if allowed:
                    link['prev'] = prev
                    self._chain[prev['element'].id]['next'] = link
            if link['prev'] is not None and (moveup is ticket.id or movedn is prev['element'].id):
                queue = component.getUtility(interfaces.IRecalculationQueue)
                queue.user = self.request.principal.id
                queue.message = translate(_(u'Moving ${type} #${no} ${action} #${no2}', mapping={'type': getObjectType(ticket),
                                                                                                 'no': moveup is ticket.id and ticket.id or prev['element'].id,
                                                                                                 'no2': movedn is prev['element'].id and prev['element'].id or ticket.id,
                                                                                                 'action': moveup is ticket.id and _(u'above') or _(u'below')}), context=self.request)
                swap_objects(ticket, prev['element'], self.resource)
                self.redirect(self.base_url())
                return [], table
            prev = link
        return new_results, table

    def filterable(self):
        return {}


class PlanProjectTickets(PlanResourceTickets):
    """ View providing the functionality to reorder the tickets of
        project and thus changing their priority
    """
    grok.context(IProject)
    grok.implements(interfaces.IPlanningView)
    navigation.menuitem(IActionsMenu, _(u'Plan tickets'))
    navigation.menuitem(IMainActionsMenu, _(u'Plan tickets'))

    def query(self):
        return query.And(set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                         query.Eq(('catalog', 'project'), self.context.id),
                         query.Eq(('catalog', 'complete'), 0))

    @property
    def caption(self):
        return u''

    @property
    def resource(self):
        return None

    def base_url(self):
        return self.url(self.context) + '/@@plan'

    def createTable(self):
        table = super(PlanProjectTickets, self).createTable()
        if IProject.providedBy(self.context):
            table.columns = [column for column in table.columns if not column[0] in ('client', 'project',)]
        return table


class PlanProjects(PlanProjectTickets):
    """ View providing the functionality to reorder whole projects
        and thus changing their priority
    """
    grok.context(IHorae)
    grok.implements(interfaces.IPlanningView)
    navigation.menuitem(IActionsMenu, _(u'Plan projects'))
    navigation.menuitem(IMainActionsMenu, _(u'Plan projects'))

    def query(self):
        return query.And(set.AnyOf(('catalog', 'implements'), [IProject.__identifier__, ]),
                         query.Eq(('catalog', 'complete'), 0))

    def results(self):
        results, table = super(PlanResourceTickets, self).results()
        self._chain = {}
        new_results = []
        prev = None
        try:
            moveup = int(self.request.form.get('moveup'))
        except:
            moveup = None
        try:
            movedn = int(self.request.form.get('movedn'))
        except:
            movedn = None
        for project in results:
            new_results.append(project)
            link = dict(element=project, next=None, prev=None)
            self._chain[project.id] = link
            if prev is not None:
                link['prev'] = prev
                self._chain[prev['element'].id]['next'] = link
            if link['prev'] is not None and (moveup is project.id or movedn is prev['element'].id):
                queue = component.getUtility(interfaces.IRecalculationQueue)
                queue.user = self.request.principal.id
                queue.message = translate(_(u'Moving ${type} #${no} ${action} #${no2}', mapping={'type': getObjectType(project),
                                                                                                 'no': moveup is project.id and project.id or prev['element'].id,
                                                                                                 'no2': movedn is prev['element'].id and prev['element'].id or project.id,
                                                                                                 'action': moveup is project.id and _(u'above') or _(u'below')}), context=self.request)
                swap_objects(project, prev['element'])
                self.redirect(self.base_url())
                return [], table
            prev = link
        if table is not None:
            table.columns = [column for column in table.columns if not column[0] in ('dependencies', 'project', 'milestone',)]
        return new_results, table


class DragAndDropHelper(grok.View):
    """ Helper view used by JavaScript for drag and drop reordering
    """
    grok.baseclass()
    grok.require('horae.Plan')
    grok.name('plan.helper')

    obj = ITicket

    # Those are here solely to have them captured by i18ndude
    order = _(u'Updating order...')
    forecast = _(u'Updating forecast...')
    update = _(u'Update')

    def __call__(self, action, resource=None, position=None):
        self.action = action
        self.position = position
        self.resource = resource
        if self.resource is not None:
            self.resource = IGlobalResources(findParentByInterface(self.context, IGlobalResourcesHolder)).get_object(self.resource)
        if self.position is not None:
            self.position = self.find_object(self.position)
            if self.position is not None and not self.position.id in self.disabled():
                if self.resource is None:
                    self.position = interfaces.IPositionedObject(self.position).position
                else:
                    self.position = component.getMultiAdapter((self.position, self.resource), interfaces.IPositionedObject).position
        if not self.action in ('disabled', 'moveup', 'movedown', 'info',):
            return '0'
        return json.dumps(getattr(self, self.action)())

    def find_object(self, id):
        results = component.getUtility(IQuery).searchResults(query.And(set.AnyOf(('catalog', 'implements'), [self.obj.__identifier__, ]),
                                                                       query.Eq(('catalog', 'id'), int(id))), limit=1)
        for obj in results:
            return obj
        return None

    def info(self):
        if self.request.form.get('ids', None) is not None:
            ids = map(int, self.request.form.get('ids').split(','))
        info = []
        results = component.getUtility(IQuery).searchResults(query.And(set.AnyOf(('catalog', 'implements'), [self.obj.__identifier__, ]),
                                                                       query.In(('catalog', 'id'), ids)))
        calculator = component.getAdapter(self.context, interfaces.ICalculator, 'simple')
        for obj in results:
            if self.resource is not None:
                start, end = calculator.entries_by_resource(obj, self.resource, True)[1:]
            else:
                start, end = calculator.entries(obj, True)[1:]
            info.append({'id': obj.id, 'forecast': render_execution(obj, self.request, start=start, end=end)})
        return info

    def disabled(self):
        return []

    def moveup(self):
        if self.position is None:
            return '0'
        move_object_above(self.obj, self.context, self.position, self.resource)
        return self.context.id

    def movedown(self):
        if self.position is None:
            return '0'
        move_object_below(self.obj, self.context, self.position, self.resource)
        return self.context.id

    def render(self):
        return u''


class TicketDragAndDropHelper(DragAndDropHelper):
    """ Helper view used by JavaScript for drag and drop reordering
    """
    grok.context(ITicket)

    def disabled(self, context=None):
        if context is None:
            context = self.context
        dependencies = ITicketDependencies(context)
        top = []
        queries = []
        for dep in dependencies.dependencies():
            top.append(interfaces.IPositionedObject(dep).position)
        if top:
            queries.append(query.Ge(('planning', 'position'), min(top)))
        bottom = []
        for dep in dependencies.dependents():
            bottom.append(interfaces.IPositionedObject(dep).position)
        if bottom:
            queries.append(query.Le(('planning', 'position'), max(bottom)))
        q = set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ])
        disabled = []
        if queries:
            if len(queries) > 1:
                q = query.And(q, query.Or(*queries))
            else:
                q = query.And(q, queries[0])
            disabled = [record.id for record in component.getUtility(IQuery).searchResults(q)]
        return disabled


class ProjectDragAndDropHelper(DragAndDropHelper):
    """ Helper view used by JavaScript for drag and drop reordering
    """
    grok.context(IProject)

    obj = IProject
