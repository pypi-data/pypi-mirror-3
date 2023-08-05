import grok

from zope import schema
from zope import component
from zope.site.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security import checkPermission
from zope.traversing.interfaces import ITraversable

from hurry import query

from horae.core import utils
from horae.lifecycle.interfaces import ILatest
from horae.autocomplete.providers import AbstractValueProvider
from horae.autocomplete.interfaces import IValueProvider, IAutocompleteField
from horae.ticketing import interfaces

MAX_RESULTS = 15
NAMES = {
    interfaces.ITicket: 'ticket',
    interfaces.IMilestone: 'milestone',
    interfaces.IProject: 'project',
    interfaces.IClient: 'client',
}


def term_factory(obj):
    return schema.vocabulary.SimpleTerm(obj.id, obj.id, '#%s %s' % (obj.id, obj.name))


def autocomplete_factory(obj):
    return (obj.id, '#%s %s' % (obj.id, obj.name))


class PropertiedValueProvider(grok.MultiAdapter, AbstractValueProvider):
    """ Base implementation of a value provider for objects
    """
    grok.baseclass()
    grok.provides(IValueProvider)
    interface = None
    permission = 'horae.View'

    def __call__(self, term):
        try:
            obj = component.getMultiAdapter((getSite(), utils.getRequest()), ITraversable, NAMES[self.interface]).traverse(term, None)
            if checkPermission(self.permission, obj):
                return [autocomplete_factory(obj), ]
        except:
            pass
        if term:
            term = '*' + '* *'.join(term.split(' ')) + '*'
        results = []
        for obj in component.getUtility(query.interfaces.IQuery).searchResults(query.And(query.Text(('catalog', 'text'), term),
                                                                                         query.set.AnyOf(('catalog', 'implements'), [self.interface.__identifier__, ])), sort_field=('catalog', 'sorting'), reverse=True):
            results.append(autocomplete_factory(obj))
            if len(results) >= MAX_RESULTS:
                break
        return results


@grok.adapter(IAutocompleteField, IBrowserRequest, name='ticket')
@grok.implementer(IValueProvider)
def tickets_value_provider(field, request):
    """ Value provider for tickets
    """
    provider = PropertiedValueProvider(field, request)
    provider.interface = interfaces.ITicket
    return provider


@grok.adapter(IAutocompleteField, IBrowserRequest, name='milestone')
@grok.implementer(IValueProvider)
def milestones_value_provider(field, request):
    """ Value provider for milestones
    """
    provider = PropertiedValueProvider(field, request)
    provider.interface = interfaces.IMilestone
    return provider


@grok.adapter(IAutocompleteField, IBrowserRequest, name='project')
@grok.implementer(IValueProvider)
def projects_value_provider(field, request):
    """ Value provider for projects
    """
    provider = PropertiedValueProvider(field, request)
    provider.interface = interfaces.IProject
    return provider


@grok.adapter(IAutocompleteField, IBrowserRequest, name='client')
@grok.implementer(IValueProvider)
def clients_value_provider(field, request):
    """ Value provider for clients
    """
    provider = PropertiedValueProvider(field, request)
    provider.interface = interfaces.IClient
    return provider


class PropertiedVocabulary(object):
    """ Base implementation of a lazy vocabulary of objects
    """
    grok.implements(schema.interfaces.IVocabularyTokenized)
    interface = None
    permission = 'horae.View'

    def __init__(self, context):
        self.context = context

    def get_obj(self, id):
        try:
            return component.getMultiAdapter((getSite(), utils.getRequest()), ITraversable, NAMES[self.interface]).traverse(id, None)
        except:
            return None

    def __contains__(self, value):
        obj = self.get_obj(value)
        if not self.interface.providedBy(obj):
            return False
        return checkPermission(self.permission, obj)

    def getTerm(self, value):
        if not value in self:
            raise LookupError(value)
        return term_factory(self.get_obj(value))

    def __iter__(self):
        try:
            request = utils.getRequest()
            principal = request.principal
            for obj in ILatest(principal).objects(self.interface):
                if obj.id in self:
                    yield term_factory(obj)
        except:
            pass

    def __len__(self):
        return 1

    def getTermByToken(self, token):
        try:
            assert token in self
            obj = component.getMultiAdapter((getSite(), utils.getRequest()), ITraversable, NAMES[self.interface]).traverse(token, None)
            return term_factory(obj)
        except:
            raise LookupError(token)


def tickets_vocabulary_factory(context):
    """ A lazy vocabulary of tickets registered as
        **horae.search.vocabulary.tickets**
    """
    vocab = PropertiedVocabulary(context)
    vocab.interface = interfaces.ITicket
    return vocab
schema.vocabulary.getVocabularyRegistry().register('horae.search.vocabulary.tickets', tickets_vocabulary_factory)


def milestones_vocabulary_factory(context):
    """ A lazy vocabulary of milestones registered as
        **horae.search.vocabulary.milestones**
    """
    vocab = PropertiedVocabulary(context)
    vocab.interface = interfaces.IMilestone
    return vocab
schema.vocabulary.getVocabularyRegistry().register('horae.search.vocabulary.milestones', milestones_vocabulary_factory)


def projects_vocabulary_factory(context):
    """ A lazy vocabulary of projects registered as
        **horae.search.vocabulary.projects**
    """
    vocab = PropertiedVocabulary(context)
    vocab.interface = interfaces.IProject
    return vocab
schema.vocabulary.getVocabularyRegistry().register('horae.search.vocabulary.projects', projects_vocabulary_factory)


def clients_vocabulary_factory(context):
    """ A lazy vocabulary of clients registered as
        **horae.search.vocabulary.clients**
    """
    vocab = PropertiedVocabulary(context)
    vocab.interface = interfaces.IClient
    return vocab
schema.vocabulary.getVocabularyRegistry().register('horae.search.vocabulary.clients', clients_vocabulary_factory)
