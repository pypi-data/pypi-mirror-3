import grok

from horae.core.interfaces import IHorae, IApplicationUpgrade
from horae.resources.interfaces import IGlobalResources, IHumanResource

from horae.planning.catalog import add_resource_index


class UpgradeStep(grok.Adapter):
    """ An upgrade step creating missing resource position indexes
    """
    grok.context(IHorae)
    grok.implements(IApplicationUpgrade)
    grok.name('horae.planning.upgrade')

    def available(self):
        return True

    def upgrade(self):
        messages = []
        for resource in IGlobalResources(self.context).objects():
            if IHumanResource.providedBy(resource):
                if add_resource_index(resource):
                    messages.append(u'created position catalog index for %s' % resource.name)
        return messages
