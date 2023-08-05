import grok

from zope import interface
from zope import component

from horae.core import utils
from horae.search.interfaces import IColumnProvider, IRowClassProvider
from horae.properties.interfaces import IPropertiedDisplayWidgetsProvider
from horae.properties import views, properties
from horae.resources.interfaces import IPlannedWorkTimeHolder
from horae.ticketing.interfaces import IProject, IMilestone, ITicket
from horae.ticketing.ticketing import Project, Milestone, Ticket

from horae.planning import _
from horae.planning import interfaces

interface.classImplements(Project, IPlannedWorkTimeHolder)
interface.classImplements(Milestone, IPlannedWorkTimeHolder)
interface.classImplements(Ticket, IPlannedWorkTimeHolder)


def render_execution(obj, request, human_resource=None, start=None, end=None):
    if start is None or end is None:
        exc = interfaces.IEstimatedExecution(obj, None)
        if exc is None:
            return u''
        if start is None:
            start = exc.start(human_resource)
        if end is None:
            end = exc.end(human_resource)
    if not start:
        return u''
    return end and utils.formatDateTimeRange(start, end, request) or utils.formatDateTime(start, request)


class EstimatedExecutionWidgetProvider(grok.Adapter):
    """ Provides estimated execution widget for a propertieds display view
    """
    grok.baseclass()
    grok.implements(IPropertiedDisplayWidgetsProvider)

    def __init__(self, context):
        self.context = context

    def widgets(self, widgets, request):
        rendered = render_execution(self.context, request)
        if not rendered:
            return widgets
        execution = properties.RichTextProperty()
        execution.id = 'execution'
        execution.name = _(u'Planned execution')
        execution.order = 0
        widgets.append(views.PropertyDisplayWidget(execution, rendered, self.context, request, None, 'planned-execution'))
        return widgets


class ProjectEstimatedExecutionWidgetProvider(EstimatedExecutionWidgetProvider):
    """ Provides estimated execution widget for a projects display view
    """
    grok.name('horae.planning.project.execution')
    grok.context(IProject)


class MilestoneEstimatedExecutionWidgetProvider(EstimatedExecutionWidgetProvider):
    """ Provides estimated execution widget for a milestones display view
    """
    grok.name('horae.planning.milestone.execution')
    grok.context(IMilestone)


class TicketEstimatedExecutionWidgetProvider(EstimatedExecutionWidgetProvider):
    """ Provides estimated execution widget for a tickets display view
    """
    grok.name('horae.planning.ticket.execution')
    grok.context(ITicket)


class ForecastWidgetProvider(grok.Adapter):
    """ Provides forecast widget for a propertieds display view
    """
    grok.baseclass()
    grok.implements(IPropertiedDisplayWidgetsProvider)

    def __init__(self, context):
        self.context = context

    def widgets(self, widgets, request):
        start, end = component.getAdapter(self.context, interfaces.ICalculator, 'simple').entries(self.context)[1:]
        rendered = render_execution(self.context, request, start=start, end=end)
        if not rendered:
            return widgets
        forecast = properties.RichTextProperty()
        forecast.id = 'forecast'
        forecast.name = _(u'Forecast')
        forecast.order = 1
        widgets.insert(0, views.PropertyDisplayWidget(forecast, rendered, self.context, request, None, 'forecast'))
        return widgets


class ProjectForecastWidgetProvider(ForecastWidgetProvider):
    """ Provides forecast widget for a projects display view
    """
    grok.name('horae.planning.project.forecast')
    grok.context(IProject)


class MilestoneForecastWidgetProvider(ForecastWidgetProvider):
    """ Provides forecast widget for a milestones display view
    """
    grok.name('horae.planning.milestone.forecast')
    grok.context(IMilestone)


class TicketForecastWidgetProvider(ForecastWidgetProvider):
    """ Provides forecast widget for a tickets display view
    """
    grok.name('horae.planning.ticket.forecast')
    grok.context(ITicket)


class ExecutionColumnProvider(grok.Adapter):
    """ Adds the estimated execution to the default table columns
    """
    grok.implements(IColumnProvider)
    grok.context(interface.Interface)
    grok.name('horae.planning.column.execution')

    name = 'execution'
    title = _(u'Planned execution')
    sortable = None
    insert_after = '*'

    def __init__(self, context):
        self.context = context

    def filterable(self):
        """ Returns a vocabulary for filtering the column or None if no filtering is available
        """
        None

    def factory(self, object, request):
        """ Returns the value to be displayed for the given object
        """
        return render_execution(object, request)

    def cache_key(self, key, *args, **kwargs):
        """ Modifies the cache key if needed and returns it
        """
        exc = interfaces.IEstimatedExecution(args[1], None)
        if exc is None:
            return key
        return key + (exc.calculated(),)


class BaseRowClassProvider(grok.Adapter):
    """ Base class to add an **overdue** CSS class if an objects due date will not be
        reached according to the current forecast
    """
    grok.baseclass()
    grok.implements(IRowClassProvider)

    def __init__(self, context):
        self.context = context

    def classes(self):
        """ Returns a list of CSS classes to be set on the row
        """
        difference = interfaces.ISearchable(self.context).difference_to_deadline
        return ['overdue', ] if difference is not None and difference < 0 else []


class ProjectRowClassProvider(BaseRowClassProvider):
    """ Adds an **overdue** CSS class if a projects due date will not be
        reached according to the current forecast
    """
    grok.context(IProject)
    grok.name('horae.planning.rowclass.project')


class MilestoneRowClassProvider(BaseRowClassProvider):
    """ Adds an **overdue** CSS class if a milestones due date will not be
        reached according to the current forecast
    """
    grok.context(IMilestone)
    grok.name('horae.planning.rowclass.milestone')


class TicketRowClassProvider(BaseRowClassProvider):
    """ Adds an **overdue** CSS class if a tickets due date will not be
        reached according to the current forecast
    """
    grok.context(ITicket)
    grok.name('horae.planning.rowclass.ticket')
