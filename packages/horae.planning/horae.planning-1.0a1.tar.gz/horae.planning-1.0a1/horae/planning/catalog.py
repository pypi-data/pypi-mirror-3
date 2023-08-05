import grok
from datetime import datetime, timedelta, MAXYEAR

from grok import index
from zope import interface
from zope import component
from zope import schema
from zope.catalog.field import FieldIndex
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest

from hurry import query

from horae.core import utils
from horae.core.interfaces import IHorae
from horae.ticketing import interfaces
from horae.search.utils import normalizeDatetime
from horae.search.interfaces import IDefaultSortingProvider, IAdvancedSearchFieldProvider
from horae.properties.interfaces import IPropertied
from horae.resources.interfaces import IPlannedResource, IPlannedResources, IHumanResource, IGlobalResourcesHolder, IGlobalResources
from horae.autocomplete import fields

from horae.planning import _
from horae.planning.interfaces import ISearchable, IPositionedObject, IEstimatedExecution, IPlanningView, ICalculator, IEstimatedExecutionRecalculated, IForecastRecalculated


class Indexes(grok.Indexes):
    """ Defines planning specific indexes
    """
    grok.site(IHorae)
    grok.context(ISearchable)
    grok.name('planning')

    plannedresources = index.Set()
    position = index.Field()
    execution_start = index.Field()
    execution_end = index.Field()
    forecast_start = index.Field()
    forecast_end = index.Field()
    difference_to_deadline = index.Field()
    deadline = index.Field()


class Searchable(grok.Adapter):
    """ Searchable ticket
    """
    grok.context(IPropertied)
    grok.implements(ISearchable)

    @property
    def plannedresources(self):
        planned = IPlannedResources(self.context, None)
        if planned is None:
            return []
        resources = []
        for resource in planned.objects():
            if resource.resource is None:
                continue
            resources.append(resource.resource.id)
        return resources

    @property
    def position(self):
        pos = IPositionedObject(self.context, None)
        if pos is not None:
            return pos.position
        return u''

    @property
    def execution_start(self):
        exc = IEstimatedExecution(self.context, None)
        if exc is not None:
            start = exc.start()
            if start is not None:
                return normalizeDatetime(start)
        return self.forecast_start

    @property
    def execution_end(self):
        exc = IEstimatedExecution(self.context, None)
        if exc is not None:
            end = exc.end()
            if end is not None:
                return normalizeDatetime(end)
        return self.forecast_end

    @property
    def forecast_start(self):
        calculator = component.getAdapter(self.context, ICalculator, 'simple')
        if calculator is not None:
            start = calculator.entries(self.context)[1]
            if start is not None:
                return normalizeDatetime(start)
        return normalizeDatetime(datetime(MAXYEAR, 12, 31))

    @property
    def forecast_end(self):
        calculator = component.getAdapter(self.context, ICalculator, 'simple')
        if calculator is not None:
            end = calculator.entries(self.context)[2]
            if end is not None:
                return normalizeDatetime(end)
        return normalizeDatetime(datetime(MAXYEAR, 12, 31))

    @property
    def difference_to_deadline(self):
        due = IEstimatedExecution(self.context).due_date()
        if due is None:
            return None
        end = self.forecast_end
        if end == normalizeDatetime(datetime(MAXYEAR, 12, 31)):
            return None
        return normalizeDatetime(due) - self.forecast_end

    @property
    def deadline(self):
        due = IEstimatedExecution(self.context).due_date()
        if due is None:
            return None
        return normalizeDatetime(due)

    def __getattr__(self, name):
        if not name.startswith('position_'):
            raise AttributeError()
        if not interfaces.ITicket.providedBy(self.context):
            return u''
        try:
            resource = IGlobalResources(utils.findParentByInterface(self.context, IGlobalResourcesHolder)).get_object(name[9:])
        except KeyError:
            return u''
        if resource is None or not IHumanResource.providedBy(resource):
            return u''
        return component.queryMultiAdapter((self.context, resource), IPositionedObject).position


class PlanningAdvancedSearchFieldProvider(grok.MultiAdapter):
    """ Provides planning related search fields
    """
    grok.adapts(interface.Interface, IBrowserRequest)
    grok.implements(IAdvancedSearchFieldProvider)
    grok.name('horae.planning.search.fields')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def fields(self):
        """ Returns a list of fields to be added to the form
        """
        return [
            schema.Int(
                __name__='deadline_within_days',
                title=_(u'Deadline within (days)'),
                required=False
            ),
            schema.Int(
                __name__='difference_to_deadline_lower_than',
                title=_(u'Forecast difference to deadline lower than (days)'),
                required=False
            ),
            fields.AutocompleteList(
                __name__='plannedresources',
                title=_(u'Planned resources'),
                required=False,
                value_type=schema.Choice(
                    vocabulary='horae.resources.vocabulary.humanresourcesid'
                )
            )
        ]

    def query(self, **data):
        """ Returns a list of queries
        """
        queries = []
        if data.get('deadline_within_days', None) is not None:
            queries.extend([query.Ge(('planning', 'deadline'), normalizeDatetime(datetime.now())),
                            query.Le(('planning', 'deadline'), normalizeDatetime(datetime.now() + timedelta(days=data['deadline_within_days'])))])
        if data.get('difference_to_deadline_lower_than', None) is not None:
            queries.append(query.Le(('planning', 'difference_to_deadline'), data['difference_to_deadline_lower_than'] * 24 * 60))
        if data.get('plannedresources', None):
            queries.append(query.set.AnyOf(('planning', 'plannedresources'), data['plannedresources']))
        return queries


class DefaultSortingProvider(grok.Adapter):
    """ Defines **execution_start** as new default sort field
    """
    grok.context(interface.Interface)
    grok.implements(IDefaultSortingProvider)

    def sort_field(self):
        """ The index used to sort
        """
        return ('planning', 'execution_start')

    def reverse(self):
        """ Whether to reverse the sort order
        """
        return 0


class PlanningDefaultSortingProvider(grok.Adapter):
    """ Defines **position** as new default sort field for planning views
    """
    grok.context(IPlanningView)
    grok.implements(IDefaultSortingProvider)

    def sort_field(self):
        """ The index used to sort
        """
        return ('planning', 'position')

    def reverse(self):
        """ Whether to reverse the sort order
        """
        return 1


class ResourceDefaultSortingProvider(grok.MultiAdapter):
    """ Defines the resource specific **position** as new default sort field
        for planning views of a human resource
    """
    grok.adapts(interface.Interface, IHumanResource)
    grok.implements(IDefaultSortingProvider)

    def __init__(self, context, resource):
        self.context = context
        self.resource = resource

    def sort_field(self):
        """ The index used to sort
        """
        return ('planning', 'position_%s' % self.resource.id)

    def reverse(self):
        """ Whether to reverse the sort order
        """
        return 1


@grok.subscribe(IHumanResource, grok.IObjectAddedEvent)
def add_resource_index(obj, event=None):
    """ Adds the resource specific position index after a new
        human resource has been added
    """
    catalog = component.getUtility(ICatalog, 'planning')
    id = 'position_%s' % obj.id
    if id in catalog:
        return False
    index = FieldIndex(field_name=id)
    index.interface = ISearchable
    catalog[id] = index
    catalog.updateIndex(index)
    return True


@grok.subscribe(IPlannedResource, grok.IObjectModifiedEvent)
@grok.subscribe(IPlannedResources, grok.IContainerModifiedEvent)
def reindex_object(obj, event=None):
    """ Reindexes the planned resources index after one has changed
    """
    ticket = utils.findParentByInterface(obj, interfaces.ITicket)
    catalog = component.getUtility(ICatalog, 'planning')
    intid = component.getUtility(IIntIds, context=catalog)
    id = intid.queryId(ticket)
    catalog['plannedresources'].index_doc(id, ticket)


@grok.subscribe(interface.Interface, IEstimatedExecutionRecalculated)
@grok.subscribe(interface.Interface, IForecastRecalculated)
def reindex_on_recalculation(obj, event):
    """ Reindexes the forecast and execution indexes after an object has
        been recalculated
    """
    catalog = component.getUtility(ICatalog, 'planning')
    intid = component.getUtility(IIntIds, context=catalog)
    id = intid.queryId(obj)
    for index in ('execution_start', 'execution_end', 'forecast_start', 'forecast_end', 'difference_to_deadline',):
        catalog[index].index_doc(id, obj)
