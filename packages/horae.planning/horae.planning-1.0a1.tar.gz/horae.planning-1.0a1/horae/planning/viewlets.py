import grok

from zope import interface
from zope import component
from zope import schema
from zope.site.hooks import getSite

from horae.core.interfaces import IHorae
from horae.auth.interfaces import IUser
from horae.layout import layout
from horae.layout.interfaces import IDisplayView
from horae.layout.viewlets import ContentBeforeManager
from horae.ticketing import viewlets
from horae.resources import _ as _r
from horae.resources.interfaces import IHumanResource, IGlobalResources

from horae.planning import _
from horae.planning.interfaces import IPlanningView, IRangedView, ITimeRangedView, IResourceCostunitRangedView

grok.templatedir('viewlet_templates')


class Name(viewlets.Name):
    """ Renders the name of the human resource
    """
    grok.context(IHumanResource)

    def update(self):
        self.name = _r(u'Resource')
        self.description = self.context.name
        self.id = None


class Description(viewlets.Description):
    """ Renders the description of the human resource
    """
    grok.context(IHumanResource)


class ResourceInfo(layout.Viewlet):
    """ Renders a list of human resources linked with the currently displayed user
    """
    grok.viewletmanager(ContentBeforeManager)
    grok.context(IUser)
    grok.view(IDisplayView)
    grok.order(50)

    def update(self):
        self.resources = []
        for resource in IGlobalResources(getSite()).objects():
            if not IHumanResource.providedBy(resource) or not resource.user == self.context.username:
                continue
            self.resources.append({
                'url': self.view.url(resource),
                'name': resource.name})
        if len(self.resources) > 1:
            self.info = _(u'The user is linked to the following human resources:')
        elif len(self.resources) == 1:
            self.info = _(u'The user is linked to the following human resource:')


class PlanProjectsTitle(viewlets.Name):
    """ Renders the title for the :py:class:`horae.planning.planning.PlanProjects` view
    """
    grok.context(IHorae)
    grok.view(IPlanningView)

    def update(self):
        self.name = _(u'Plan open projects')
        self.description = None
        self.id = None


class RangeSelectionForm(layout.Form):
    """ Form for selecting a date range and optionally a resource or cost unit
    """
    grok.context(interface.Interface)
    grok.name('rangeselection')
    id = 'range-selection'

    _timerange = False
    _start = None
    _end = None

    _resource_costunit = False
    _resource = None
    _costunit = None

    def set_range(self, start, end):
        self._start = start.date()
        self._end = end.date()
        self._timerange = True

    def set_resource_costunit(self, resource, costunit):
        self._resource = resource
        self._costunit = costunit
        self._resource_costunit = True

    def update(self):
        fields = {}
        if self._timerange:
            fields.update(dict(
                start=schema.Date(
                    title=_(u'Start'),
                    required=False,
                    default=self._start
                ),
                end=schema.Date(
                    title=_(u'End'),
                    required=False,
                    default=self._end
                )
            ))
        if self._resource_costunit:
            fields.update(dict(
                resource=schema.Choice(
                    title=_r(u'Resource'),
                    required=False,
                    default=self._resource,
                    vocabulary='horae.resources.vocabulary.humanresources'
                ),
                costunit=schema.Choice(
                    title=_r(u'Cost unit'),
                    required=False,
                    default=self._costunit,
                    vocabulary='horae.resources.vocabulary.costunits'
                )
            ))
        self.form_fields = grok.Fields(**fields)

    @grok.action(_(u'Show'))
    def handle_show(self, **data):
        pass


class TimeRangeSelection(layout.Viewlet):
    """ Renders the :py:class:`RangeSelectionForm` to enable selection
        of date range, resource and cost unit for views implementing
        :py:class:`horae.planning.interfaces.IRangedView`
    """
    grok.context(interface.Interface)
    grok.viewletmanager(viewlets.ContentBeforeManager)
    grok.view(IRangedView)
    grok.name('horae.planning.rangeselection')
    grok.order(50)

    def render(self):
        form = component.getMultiAdapter((self.context, self.request), name='rangeselection')
        if ITimeRangedView.providedBy(self.view):
            form.set_range(*self.view.range())
        if IResourceCostunitRangedView.providedBy(self.view):
            form.set_resource_costunit(self.view.resource, self.view.costunit)
        return form(plain=True)
