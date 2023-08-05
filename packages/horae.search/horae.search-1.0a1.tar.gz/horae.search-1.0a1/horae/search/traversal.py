import grok

from zope import component
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IRequest

from hurry import query
from hurry.query import set

from horae.core.interfaces import IHorae
from horae.ticketing import interfaces


class BaseNamespaceTraverser(grok.MultiAdapter):
    """ Base namespace traverser
    """
    grok.baseclass()
    grok.adapts(IHorae, IRequest)
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        results = component.getUtility(query.interfaces.IQuery).searchResults(
            query.And(
                query.Eq(('catalog', 'id'), int(name)),
                set.AnyOf(('catalog', 'implements'), [self.interface.__identifier__, ])
            )
        )
        for result in results:
            return result


class ClientNamespaceTraverser(BaseNamespaceTraverser):
    grok.name('client')
    interface = interfaces.IClient


class ProjectNamespaceTraverser(BaseNamespaceTraverser):
    grok.name('project')
    interface = interfaces.IProject


class MilestoneNamespaceTraverser(BaseNamespaceTraverser):
    grok.name('milestone')
    interface = interfaces.IMilestone


class TicketNamespaceTraverser(BaseNamespaceTraverser):
    grok.name('ticket')
    interface = interfaces.ITicket
