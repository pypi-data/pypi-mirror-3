import grok

from horae.core.interfaces import IHorae, IApplicationUpgrade

from horae.search.catalog import createDefaultPropertyIndexes


class UpgradeStep(grok.Adapter):
    """ Upgrade step creating missing indexes for default properties
    """
    grok.context(IHorae)
    grok.implements(IApplicationUpgrade)
    grok.name('horae.search.upgrade')

    def available(self):
        return True

    def upgrade(self):
        return ['created catalog index for %s' % field for field in createDefaultPropertyIndexes(self.context)]
