import grok

from zope.interface import Interface
from fanstatic import Library, Resource

from js import jqueryui

from horae.js.jqplot import resource as jqplot
from horae.layout import interfaces
from horae.layout import resource

library = Library('horae.planning', 'static')

style = Resource(library, 'planning.css')
plan = Resource(library, 'plan.js', depends=[jqueryui.jqueryui, jqueryui.smoothness, resource.dialogs, resource.initialization])
graph = Resource(library, 'graph.js', depends=[jqueryui.jqueryui,
                                               jqueryui.smoothness,
                                               jqplot.style,
                                               jqplot.barRenderer,
                                               jqplot.highlighter,
                                               jqplot.enhancedLegendRenderer,
                                               jqplot.dateAxisRenderer,
                                               jqplot.categoryAxisRenderer,
                                               jqplot.canvasTextRenderer,
                                               jqplot.canvasAxisTickRenderer,
                                               jqplot.pointLabels,
                                               jqplot.cursor,
                                               resource.i18n,
                                               resource.jqplot,
                                               resource.initialization])


@grok.adapter(Interface, name='horae.planning')
@grok.implementer(interfaces.IResourceProvider)
def planning_resource_provider(context):
    """ Provides CSS and JavaScript resources needed for the
        horae.planning package
    """
    return [style, plan]
