import grok

from zope.interface import Interface
from zope.component import getMultiAdapter

from horae.layout import resource
from horae.layout import layout
from horae.layout.viewlets import HeaderRightManager

from horae.search import _
from horae.search.interfaces import ISearchForm


class Search(layout.Viewlet):
    """ Renders the :py:class:`horae.search.search.SearchForm`
    """
    grok.viewletmanager(HeaderRightManager)
    grok.context(Interface)
    grok.order(10)
    grok.require('zope.View')

    def render(self):
        view = getMultiAdapter((self.context, self.request), name='searchform')
        view.label = None
        view.text_label = _(u'Search...')
        view.form_fields = grok.AutoFields(ISearchForm).omit('implements', 'current')
        rendered = view(plain=True)
        return rendered is not None and rendered or u''

    def update(self):
        resource.search.need()
