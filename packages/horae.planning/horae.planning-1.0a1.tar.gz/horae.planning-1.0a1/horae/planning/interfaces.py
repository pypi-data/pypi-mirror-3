from zope import interface
from zope import schema
from zope.component.interfaces import IObjectEvent

from horae.core.interfaces import IDeferred
from horae.resources.interfaces import IResourceCostunit
from horae.timeaware.interfaces import ITimeAware, ITimeEntry

from horae.planning import _


class IPositionableObject(interface.Interface):
    """ An object which may be positioned
    """


class IPositionedObject(interface.Interface):
    """ A positioned object
    """

    position = interface.Attribute('position')


class IPositionChangedEvent(IObjectEvent):
    """ An objects position has been changed
    """


class ISearchable(interface.Interface):
    """ Searchable ticket
    """

    plannedresources = interface.Attribute('plannedresources')
    position = interface.Attribute('position')
    execution_start = interface.Attribute('execution_start')
    execution_end = interface.Attribute('execution_end')
    forecast_start = interface.Attribute('forecast_start')
    forecast_end = interface.Attribute('forecast_end')
    difference_to_deadline = interface.Attribute('difference_to_deadline')
    deadline = interface.Attribute('deadline')


class IPlanningView(interface.Interface):
    """ Marker interface for planning views
    """


class IEstimationTimeEntry(ITimeEntry):
    """ A time entry additionally holding information about the associated resource and cost unit
    """

    resourcecostunit = schema.Object(
        required=True,
        schema=IResourceCostunit
    )

    ticket = schema.Int(required=True)
    milestone = schema.Int(required=False)
    project = schema.Int(required=True)
    client = schema.Int(required=True)


class IWorkExpenseEntry(ITimeEntry):
    """ Marker interface for entries coming from work expenses
    """


class IEstimatedExecution(ITimeAware):
    """ Information about the estimated execution of a given object
    """

    def hours(daterange=None, human_resource=None, costunit=None, default=None):
        """ Returns the sum of the hours of the contained time entries, optionally only for a given human resource
            or cost unit
        """

    def start(human_resource=None, costunit=None, default=None):
        """ Returns the estimated start date and time, optionally only for a given human resource
            or cost unit
        """

    def end(human_resource=None, costunit=None, default=None):
        """ Returns the estimated end date and time, optionally only for a given human resource
            or cost unit
        """

    def objects(daterange=None, human_resource=None, costunit=None):
        """ Returns a list of all contained time entries, optionally only for a given human resource
            or cost unit
        """

    def entries(daterange=None, human_resource=None, costunit=None):
        """ Returns a list of non repeating time entries to cover the provided date range,
            optionally only for a given human resource or cost unit
        """

    def calculated():
        """ The date and time of the calculation
        """

    def user():
        """ The user who issued the calculation or None
        """

    def message():
        """ The optional message added to the calculation
        """

    def due_date():
        """ Returns the due date set on either the ticket, milestone or project.
            Returns None if no due date was found.
        """


class ICachedEstimatedExecution(IEstimatedExecution):
    """ Cached information about the estimated execution of a given object
    """

    def recalculate(user=None, message=None):
        """ Recalculates the different entries and dates optionally marked by a username and annotated with a message
        """

    def history_entry():
        """ Creates a new entry in the history
        """

    def history_before(date):
        """ Returns an IEstimatedExecution containing the information of the last history entry before the given date
            or None if no entry was found
        """

    def history_dates(hidden=False):
        """ Returns a list of dates of the available history entries
        """

    def hide_history_entry(date):
        """ Marks a specific history entry as hidden
        """

    def show_history_entries():
        """ Marks all history entries as visible
        """

    def clear_history():
        """ Clears the history
        """


class IEstimatedExecutionRecalculated(IObjectEvent):
    """ The estimated execution of an object has been recalculated
    """


class IEstimatedExecutionOfObject(ITimeAware):
    """ Information about estimated execution of an object
    """

    def hours(daterange=None, ticket=None, milestone=None, project=None, client=None):
        """ Returns the sum of the hours of the contained time entries,
            optionally only for a given ticket, milestone, project or client
        """

    def start(ticket=None, milestone=None, project=None, client=None):
        """ Returns the estimated start date and time,
            optionally only for a given ticket, milestone, project or client
        """

    def end(ticket=None, milestone=None, project=None, client=None):
        """ Returns the estimated end date and time,
            optionally only for a given ticket, milestone, project or client
        """

    def objects(daterange=None, ticket=None, milestone=None, project=None, client=None):
        """ Returns a list of all contained time entries,
            optionally only for a given ticket, milestone, project or client
        """

    def entries(daterange=None, ticket=None, milestone=None, project=None, client=None):
        """ Returns a list of non repeating time entries to cover the provided date range,
            optionally only for a given ticket, milestone, project or client
        """


class ICachedEstimatedExecutionOfObject(IEstimatedExecutionOfObject):
    """ Cached information about estimated execution of an object
    """

    def remove(ticket=None, milestone=None, project=None, client=None):
        """ Removes the stored entries for a given ticket, milestone, project or client
        """

    def history_entry(date=None):
        """ Creates a new entry in the history optionally for a given date
        """

    def history_before(date):
        """ Returns an IEstimatedExecutionOfObject containing the information of the last history entry before the given date
            or None if no entry was found
        """

    def history_dates(hidden=False):
        """ Returns a list of dates of the available history entries
        """

    def hide_history_entry(date):
        """ Marks a specific history entry as hidden
        """

    def show_history_entries():
        """ Marks all history entries as visible
        """

    def clear_history():
        """ Clears the history
        """


class IRecalculationForm(interface.Interface):
    """ Recalculation form
    """

    message = schema.Text(
        title=_(u'Message'),
        description=_(u'A short message describing the cause of the recalculation'),
        required=False
    )


class IRangedView(interface.Interface):
    """ A ranged view
    """


class ITimeRangedView(IRangedView):
    """ View accepting a user defined time range
    """

    default_range = interface.Attribute('default_range')

    def range():
        """ Returns the range (start date, end date tuple) currently displayed by the view
        """


class IResourceCostunitRangedView(IRangedView):
    """ View accepting a user defined resource and costunit
    """

    resource = interface.Attribute('resource')
    costunit = interface.Attribute('costunit')


class ICalculator(interface.Interface):
    """ Calculates execution of a ticket
    """

    title = interface.Attribute('title')
    cssClass = interface.Attribute('cssClass')

    def worktime(ticket, resource):
        """ Returns the work time for the given ticket and resource
        """

    def effective(ticket, resource, costunit):
        """ Returns the effective worked time of the given ticket, resource and cost unit
        """

    def absence(resource):
        """ Returns the absence of the given resource
        """

    def estimated_hours(ticket, planned_resource):
        """ Returns the estimated hours for the planned resource
        """

    def fetch_entries(ticket):
        """ Returns whether to fetch new entries from the work time or not
        """

    def complete(ticket):
        """ Returns whether this ticket is completed or not
        """

    def planned_resources(ticket):
        """ Returns the planned resources for the given ticket
        """

    def start(possible_start, start):
        """ Returns the start date
        """

    def planned_worktime(ticket):
        """ Returns a ITimeAware holding the planned work time set on either
            the ticket, milestone or project. Returns None if no work time is
            planned
        """

    def minimum_entry_length(ticket):
        """ Returns the minimum entry length for the ticket
        """

    def max_week_hours(ticket):
        """ Returns the maximum week hours for the ticket
        """

    def possible_start(ticket):
        """ Returns the possible start set on either the ticket, milestone or project
            or given by a dependency. Returns None if no start date was found.
        """

    def resource_costunit_map(ticket):
        """ Returns a dictionary keyed by resourceid, costunitid tuples holding a list
            of ITimeEntry objects representing the already registered work time for the
            ticket
        """

    def calculate(hours, start, worktime, absence=None, initial_entries=[], min_length=0.0, max_week_hours=None, fetch_entries=True):
        """ Iterator of ITimeEntry objects
        """

    def tickets(resource):
        """ Iterator over the ordered tickets for a given resource
        """

    def entries_by_planned_resource(obj, planned_resource, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given object and planned resource
        """

    def entries_by_resource(obj, resource, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given object and resource
        """

    def entries(obj, recalculate=False):
        """ Returns a ITimeAware holding the calculated time entries and start and end date for the given object
        """

    def available(ticket, planned_resource):
        """ Whether this calculation is available for the given ticket and planned_resource
        """


class ICachedCalculator(ICalculator):
    """ Calculates execution of a ticket and caches them
    """

    def calculated():
        """ Returns the date of the last calculation
        """

    def mark_calculation():
        """ Sets the calculation date to today
        """

    def invalidate_all(clear_cache=True):
        """ Invalidates all cached calculations
        """

    def invalidate(obj):
        """ Invalidates the cache for the given obj
        """

    def clear_cache(method=None):
        """ Clear the cache of the calculator, optionally only for a given method
        """


class IForecastRecalculated(IObjectEvent):
    """ The forecast of an object has been recalculated
    """


class IDeferredInvalidator(IDeferred):
    """ Utility handling deferred calculation invalidation
    """
