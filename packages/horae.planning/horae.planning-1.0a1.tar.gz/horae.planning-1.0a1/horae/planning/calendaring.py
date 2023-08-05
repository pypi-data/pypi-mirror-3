import grok

from zope import component

from hurry.query.interfaces import IQuery
from hurry.query import query, set

from horae.core.utils import formatDateTime, findParentByInterface
from horae.core.interfaces import ICurrencyFormatter
from horae.calendar.interfaces import ICalendarEntries
from horae.resources.interfaces import IHumanResource, IGlobalResourcesHolder, IGlobalResources
from horae.ticketing.interfaces import ITicket, IMilestone, IProject, IClient
from horae.auth.interfaces import IUser
from horae.timeaware import timeaware

from horae.planning import interfaces


class ResourceCalendarEntries(grok.Adapter):
    """ Provider for calendar entries of a human resource
    """
    grok.context(IHumanResource)
    grok.implements(ICalendarEntries)

    iface = interfaces.ICachedEstimatedExecutionOfObject
    cssClass = ''

    def __init__(self, context):
        super(ResourceCalendarEntries, self).__init__(context)
        self.aware = self.iface(context)
        self._ticket = {}
        self._currency = None

    def _find_ticket(self, id):
        if id in self._ticket:
            return self._ticket[id]
        results = component.getUtility(IQuery).searchResults(query.And(set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                                                                       query.Eq(('catalog', 'id'), int(id))), limit=1)
        for obj in results:
            self._ticket[id] = obj
            return obj
        self._ticket[id] = None
        return None

    def entries(self, daterange):
        return self.aware.objects(daterange)

    def render(self, entry, request, format):
        """ Renders the given entry
        """
        costunit = ''
        additional = []
        if hasattr(entry, 'resourcecostunit'):
            resourcecostunit = entry.resourcecostunit()
            if resourcecostunit is not None:
                if self._currency is None:
                    self._currency = component.getMultiAdapter((self.context, request), ICurrencyFormatter)
                costunit = '%s (%s)' % (resourcecostunit.costunit_name, self._currency.format(resourcecostunit.costunit_rate))
            if format == 'month':
                costunit += ', '
            else:
                additional.append(resourcecostunit.resource.name)
                additional.append(costunit)
        if hasattr(entry, 'ticket') is not None:
            ticket = self._find_ticket(entry.ticket)
            if ticket is not None:
                if not format == 'month':
                    project = findParentByInterface(ticket, IProject)
                    client = findParentByInterface(project, IClient)
                    additional.append('<a href="%s">%s</a>' % (grok.url(request, client), client.name))
                    additional.append('<a href="%s">%s</a>' % (grok.url(request, project), project.name))
                    if ticket.milestone is not None:
                        additional.append('<a href="%s">%s</a>' % (grok.url(request, ticket.milestone), ticket.milestone.name))
                if format == 'month':
                    return '<a href="%s" title="%s%s - %s">%s <span class="id">#%s</span></a>' % (grok.url(request, ticket), costunit, formatDateTime(entry.date_start, request, ('dateTime', 'short'), False), formatDateTime(entry.date_end, request, ('dateTime', 'short'), False), ticket.name, ticket.id), u''
                return '<strong><a href="%s" title="%s - %s">%s <span class="id">#%s</span></a></strong><br>%s' % (grok.url(request, ticket), formatDateTime(entry.date_start, request, ('dateTime', 'short'), False), formatDateTime(entry.date_end, request, ('dateTime', 'short'), False), ticket.name, ticket.id, '<br>'.join(additional)), u''
        return u'', u''


class UserCalendarEntries(ResourceCalendarEntries):
    """ Provider for calendar entries of a user
    """
    grok.context(IUser)

    def __init__(self, context):
        super(ResourceCalendarEntries, self).__init__(context)
        self.aware = timeaware.TimeAware()
        resources = IGlobalResources(findParentByInterface(self.context, IGlobalResourcesHolder))
        for resource in resources.objects():
            if not IHumanResource.providedBy(resource) or \
               not resource.user == self.context.username:
                continue
            self.aware += interfaces.ICachedEstimatedExecutionOfObject(resource)
        self._ticket = {}
        self._currency = None


class ClientCalendarEntries(ResourceCalendarEntries):
    """ Provider for calendar entries of a client
    """
    grok.context(IClient)
    iface = interfaces.IEstimatedExecution


class ProjectCalendarEntries(ResourceCalendarEntries):
    """ Provider for calendar entries of a project
    """
    grok.context(IProject)
    iface = interfaces.IEstimatedExecution


class MilestoneCalendarEntries(ResourceCalendarEntries):
    """ Provider for calendar entries of a milestone
    """
    grok.context(IMilestone)
    iface = interfaces.IEstimatedExecution


class TicketCalendarEntries(ResourceCalendarEntries):
    """ Provider for calendar entries of a ticket
    """
    grok.context(ITicket)
    iface = interfaces.IEstimatedExecution
