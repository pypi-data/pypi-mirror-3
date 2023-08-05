import grok
import json
import inspect
from datetime import date

from grokcore import message

from zope import interface
from zope import component
from zope.i18n import translate
from zope.i18n.interfaces import INegotiator, ITranslationDomain
from zope.schema import vocabulary
from zope.catalog.interfaces import ICatalog
from zope.session.interfaces import ISession
from zope.location.interfaces import ILocationInfo

from plone.memoize import ram
from megrok import navigation
from hurry import query

from horae.core.utils import formatDateTime, findParentByInterface
from horae.core.interfaces import IHorae
from horae.auth.utils import displayUser
from horae.properties.interfaces import IPropertied, IComplete, IOffer, IDefaultProperty
from horae.properties import _ as _p
from horae.ticketing import utils
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket
from horae.layout import layout
from horae.layout.interfaces import IMainNavigation, IGlobalManageMenu

from horae.search import _
from horae.search import interfaces
from horae.search.catalog import createDefaultPropertyIndexes


def row_factory_cache_key(method, *args, **kwargs):
    langs = component.getUtility(ITranslationDomain, 'horae.core').getCatalogsInfo().keys()
    langs.append('en')
    lang = component.getUtility(INegotiator).getLanguage(langs, args[0].request)
    key = (method.__module__, method.__name__, args[1], args[1].modification_date, args[2], args[0].request.getURL(), lang, date.today())
    providers = component.getAdapters((args[1],), interfaces.IColumnProvider)
    for name, provider in providers:
        key = provider.cache_key(key, *args, **kwargs)
    return key


class SearchForm(layout.Form):
    """ Simple search form allowing full text searches
        optionally only for a defined set of object types
        and only in a defined context
    """
    grok.context(interface.Interface)
    grok.require('zope.View')
    action = 'search'
    cssClass = 'search-form'

    form_fields = grok.AutoFields(interfaces.ISearchForm)
    text_label = None

    def __init__(self, *args, **kw):
        super(SearchForm, self).__init__(*args, **kw)
        self.text_label = None

    def setUpWidgets(self, ignore_request=False):
        super(SearchForm, self).setUpWidgets(ignore_request)
        session = ISession(self.request)['search']
        if self.form_fields.get('text', None) is not None:
            if self.text_label is not None:
                self.widgets['text'].label = self.text_label
            self.widgets['text'].setRenderedValue(session.get('text', ''))
        if self.form_fields.get('implements', None) is not None:
            self.widgets['implements'].setRenderedValue(session.get('implements', ''))
        if self.form_fields.get('current', None) is not None:
            self.widgets['current'].setRenderedValue(session.get('current', ''))

    @grok.action(_(u'Search'))
    def handle_search(self, **data):
        pass


class SearchMixin(object):
    """ Mix in class for views displaying search results
    """
    caption = u''
    reset_table = False
    no_results_msg = u''
    limit = None
    page_size = 20

    @ram.cache(row_factory_cache_key)
    def row_factory(self, object, columns, request):
        row = {'id': '<a href="%(url)s">%(name)s</a>' % dict(url=grok.url(request, object), name=object.id),
               'name': '<a href="%(url)s">%(name)s</a>' % dict(url=grok.url(request, object), name=object.name),
               'modifier': displayUser(object.modifier),
               'modification_date': formatDateTime(object.modification_date, self.request, ('dateTime', 'short')),
               'type': utils.getObjectType(object)}
        classes = []
        providers = component.getAdapters((object,), interfaces.IRowClassProvider)
        for name, provider in providers:
            classes.extend(provider.classes())
        providers = component.getAdapters((object,), interfaces.IColumnProvider)
        for name, provider in providers:
            row[provider.name] = provider.factory(object, request)
        row['cssClass'] = ' '.join(classes)
        return row

    @ram.cache(lambda method, *args, **kwargs: (method.__module__, method.__name__, args[1]))
    def field_catalog_map(self, field):
        names = []
        for cls in inspect.getmro(interfaces.ISearchable):
            names.extend(cls.names())
        if field in names:
            return ('catalog', field)
        return ('properties', field)

    def query(self):
        raise NotImplementedError(u'concrete classes must implement query()')

    def base_url(self):
        return grok.url(self.request, self.context) + '/search'

    def session_key(self):
        return None

    def searchArguments(self, table=None):
        sort, reverse = None, None
        if table is not None:
            sort, reverse = table.sorting()
        kw = {}
        if sort:
            kw['sort_field'] = self.field_catalog_map(sort)
        else:
            provider = component.queryMultiAdapter((self, self.context), interfaces.IDefaultSortingProvider)
            if provider is None:
                provider = interfaces.IDefaultSortingProvider(self, None)
            if provider is not None:
                kw['sort_field'] = provider.sort_field()
                reverse = provider.reverse()
            else:
                kw['sort_field'] = self.field_catalog_map('sorting')
                reverse = 1
        if reverse:
            kw['reverse'] = reverse
        if self.limit:
            kw['limit'] = self.limit
        return kw

    def createTable(self):
        table = component.getMultiAdapter((self.context, self.request), name='table')
        table.page_size = self.page_size
        table.columns = [('id', _(u'ID')), ('name', _(u'Name')), ('type', _(u'Type')), ('modifier', _(u'Last modified by')), ('modification_date', _(u'Last modified'))]
        sortable = ['id', 'type', 'modifier', 'modification_date']
        table.sortable = dict(zip(sortable, sortable))
        table.sortable['name'] = 'sortable_name'
        table.filterable = self.filterable()
        table.base_url = self.base_url()
        table.session_key = self.session_key()
        table.caption = self.caption
        table.row_factory = self.row_factory
        providers = component.getAdapters((self.context,), interfaces.IColumnProvider)
        for name, provider in providers:
            filterable = provider.filterable()
            if filterable is not None:
                table.filterable[provider.name] = filterable
            if provider.sortable:
                table.sortable[provider.name] = provider.sortable
            if provider.insert_after is None:
                table.columns.insert(0, (provider.name, provider.title))
            elif provider.insert_after in dict(table.columns).keys():
                table.columns.insert(dict(table.columns).keys().index(provider.insert_after), (provider.name, provider.title))
            else:
                table.columns.append((provider.name, provider.title))
        return table

    def filterable(self):
        filterable = {}
        filterable['type'] = vocabulary.SimpleVocabulary([
            vocabulary.SimpleTerm(0, IClient.__identifier__, utils.getObjectType(IClient)),
            vocabulary.SimpleTerm(1, IProject.__identifier__, utils.getObjectType(IProject)),
            vocabulary.SimpleTerm(2, IMilestone.__identifier__, utils.getObjectType(IMilestone)),
            vocabulary.SimpleTerm(3, ITicket.__identifier__, utils.getObjectType(ITicket))
        ])
        filterable['modifier'] = vocabulary.getVocabularyRegistry().get(self.context, 'horae.auth.vocabulary.usernames')
        return filterable

    def filtering(self, table):
        filtering = table.filtering()
        queries = []
        if filtering is None:
            return queries
        for column, value in filtering:
            queries.append(query.In(self.field_catalog_map(column), value))
        return queries

    def results(self, plain=False):
        q = self.query()
        if not q:
            return None, None
        table = None
        filter = []
        if not plain:
            table = self.createTable()
            if self.reset_table:
                table.reset()
            filter = self.filtering(table)
            if len(filter):
                q = query.And(q, *filter)
        results = component.getUtility(query.interfaces.IQuery).searchResults(q, **self.searchArguments(table))
        if not len(results) and len(filter):
            message.send(_(u'The selected filters did not match any record and have been ignored.'), u'error', u'session')
            results = component.getUtility(query.interfaces.IQuery).searchResults(self.query(), **self.searchArguments(table))
        return results, table

    def table(self):
        results, table = self.results()
        if results is None:
            return ''
        if not results and self.no_results_msg:
            return '<p class="discreet">%s</p>' % translate(self.no_results_msg, context=self.request)
        table.rows = results
        return table()


class Search(SearchForm, SearchMixin):
    """ View displaying the search form and the found results
    """
    grok.context(interface.Interface)
    grok.require('zope.View')

    label = _(u'Search')
    caption = _(u'Results')
    no_results_msg = _(u'No matching results found')

    def query_data(self):
        return ISession(self.request)['search']

    def query(self):
        session = self.query_data()
        if not ('text' in session or 'implements' in session or 'current' in session):
            return None
        queries = []
        if 'text' in session:
            try:
                id = int(session['text'])
                queries.append(query.Eq(('catalog', 'id'), id))
            except:
                queries.append(query.Text(('catalog', 'text'), '*' + '* *'.join(session['text'].split(' ')) + '*'))
        if 'implements' in session:
            queries.append(query.set.AnyOf(('catalog', 'implements'), session['implements']))
        if 'current' in session:
            context = findParentByInterface(self.context, IPropertied)
            if context is None:
                context = findParentByInterface(self.context, IHorae)
            queries.append(query.set.AnyOf(('catalog', 'path'), [ILocationInfo(context).getPath(), ]))
        return query.And(*queries)

    def append(self):
        return self.rendered

    def update_form(self, plain=False):
        self.limit = None
        self.reset_table = False
        super(Search, self).update_form()
        self.form_reset = False
        if not plain:
            self.rendered = self.table()

    def search(self, **data):
        session = ISession(self.request)['search']
        for key in ('text', 'implements', 'current'):
            if key in data and data[key]:
                session[key] = data[key]
            elif key in session:
                del session[key]
        self.reset_table = True
        self.setUpWidgets()

    @grok.action(_(u'Search'))
    def handle_search(self, **data):
        self.search(**data)


class LiveSearch(grok.View):
    """ View returning JSON output of the search results
    """
    grok.context(interface.Interface)
    grok.require('zope.View')

    def render(self):
        search = component.getMultiAdapter((self.context, self.request), name='search')
        search.update()
        search.update_form(True)
        search.limit = 11
        result = {}
        results, table = search.results(plain=True)
        if results is not None:
            if not results:
                result['message'] = '<p class="discreet">%s</p>' % translate(_(u'No matching results found'), context=self.request)
            if len(results) > 10:
                result['message'] = '<p class="discreet"><a href="search">%s</a></p>' % translate(_(u'More...'), context=self.request)
            result['results'] = []
            for obj in results:
                result['results'].append({'id': obj.id,
                                          'name': obj.name,
                                          'type': translate(utils.getObjectType(obj), context=self.request),
                                          'url': self.url(obj)})
                if len(result['results']) >= 10:
                    break
        return json.dumps(result)


class BaseAdvancedSearch(Search):
    """ Base implementation of the advanced search view
    """
    grok.baseclass()
    label = _(u'Advanced search')
    action = 'advancedsearch'
    form_fields = grok.AutoFields(interfaces.IAdvancedSearchForm)

    def base_url(self):
        return grok.url(self.request, self.context) + '/advancedsearch'

    def indexers(self):
        catalog = component.getUtility(ICatalog, 'properties')
        seen = []
        for index in catalog.values():
            property = getattr(index, 'property', None)
            if hasattr(index, 'property_name'):
                property = component.queryUtility(IDefaultProperty, name=index.property_name)
            if property is None or \
               not property.searchable or \
               property.id in seen:
                continue
            indexer = interfaces.ISearchableProperty(property, None)
            if indexer is not None:
                yield indexer
                seen.append(property.id)

    def providers(self):
        for name, provider in component.getAdapters((self.context, self.request), interfaces.IAdvancedSearchFieldProvider):
            yield provider

    def query(self):
        catalog = component.getUtility(ICatalog, 'properties')
        session = self.query_data()
        queries = []
        for indexer in self.indexers():
            data = {}
            for field in indexer.fields(catalog, self.context, self.request):
                data[field.__name__] = session.get(field.__name__, None)
                q = indexer.query(**data)
                if q is not None:
                    queries.append(q)
        for provider in self.providers():
            data = {}
            for field in provider.fields():
                data[field.__name__] = session.get(field.__name__, None)
            queries.extend(provider.query(**data))
        base = super(BaseAdvancedSearch, self).query()
        if base is not None:
            queries.append(base)
        for key, factory in (('complete', query.Eq), ('offer', query.Eq), ('client', query.In), ('project', query.In), ('milestone', query.In)):
            if key in session and (not factory is query.In or session[key]):
                queries.append(factory(('catalog', key), session[key]))
        return query.And(*queries)

    def update(self):
        catalog = component.getUtility(ICatalog, 'properties')
        fields = []
        for indexer in self.indexers():
            for field in indexer.fields(catalog, self.context, self.request):
                fields.append((field.__name__, field))
        for provider in self.providers():
            for field in provider.fields():
                fields.append((field.__name__, field))
        self.form_fields = self.form_fields + grok.Fields(**dict(fields))
        super(BaseAdvancedSearch, self).update()
        for indexer in self.indexers():
            indexer.update(self)

    def search(self, **data):
        catalog = component.getUtility(ICatalog, 'properties')
        session = ISession(self.request)['search']
        for indexer in self.indexers():
            for field in indexer.fields(catalog, self.context, self.request):
                if field.__name__ in data and data[field.__name__]:
                    session[field.__name__] = data[field.__name__]
                elif field.__name__ in session:
                    del session[field.__name__]
                del data[field.__name__]
        for provider in self.providers():
            for field in provider.fields():
                if field.__name__ in data and data[field.__name__]:
                    session[field.__name__] = data[field.__name__]
                elif field.__name__ in session:
                    del session[field.__name__]
                del data[field.__name__]
        for key in ('complete', 'offer', 'client', 'project', 'milestone'):
            if key in data and data[key] is not None:
                session[key] = data[key]
            elif key in session:
                del session[key]
        super(BaseAdvancedSearch, self).search(**data)

    def setUpWidgets(self, ignore_request=False):
        super(BaseAdvancedSearch, self).setUpWidgets(ignore_request)
        session = ISession(self.request)['search']
        for widget in self.widgets:
            if not widget.hasInput() or ignore_request:
                widget.setRenderedValue(session.get(widget.context.__name__, None))


class AdvancedSearch(BaseAdvancedSearch):
    """ View rendering the advanced search form and the search results
    """
    navigation.menuitem(IMainNavigation, _(u'Advanced search'), order=20)


class UpdateCatalog(layout.View):
    """ View to update the catalog
    """
    grok.context(IHorae)
    grok.require('horae.Manage')
    grok.name('update-catalog')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Update catalog'))

    def __call__(self):
        createDefaultPropertyIndexes(self.context)
        catalogs = component.getAllUtilitiesRegisteredFor(ICatalog)
        for cat in catalogs:
            cat.updateIndexes()
        self.redirect(self.request.get('HTTP_REFERER', self.url(self.context)))
        message.send(_(u'Catalog successfully updated'), u'info', u'session')

    def render(self):
        return ''


class BaseRowClassProvider(grok.Adapter):
    """ Base implementation of a row class provider adding CSS classes
        for objects which are completed or in an offer state
    """
    grok.baseclass()
    grok.implements(interfaces.IRowClassProvider)

    def classes(self):
        """ Returns a list of CSS classes to be set on the row
        """
        classes = []
        if IComplete(self.context, lambda: False)():
            classes.append('complete')
        if IOffer(self.context, lambda: False)():
            classes.append('offer')
        return classes


class ClientRowClassProvider(BaseRowClassProvider):
    """ Complete and offer row class provider for clients
    """
    grok.context(IClient)
    grok.name('horae.search.rowclass.client')


class ProjectRowClassProvider(BaseRowClassProvider):
    """ Complete and offer row class provider for projects
    """
    grok.context(IProject)
    grok.name('horae.search.rowclass.project')


class MilestoneRowClassProvider(BaseRowClassProvider):
    """ Complete and offer row class provider for milestones
    """
    grok.context(IMilestone)
    grok.name('horae.search.rowclass.milestone')


class TicketRowClassProvider(BaseRowClassProvider):
    """ Complete and offer row class provider for tickets
    """
    grok.context(ITicket)
    grok.name('horae.search.rowclass.ticket')


def parents_modification_cache_key(context):
    parent = context
    key = []
    while True:
        parent = findParentByInterface(parent, IPropertied, 1)
        if parent is None:
            break
        key.append(parent.modification_date)
    return tuple(key)


class CompleteColumnProvider(grok.Adapter):
    """ Column provider adding the complete column
    """
    grok.implements(interfaces.IColumnProvider)
    grok.context(interface.Interface)
    grok.name('horae.search.column.complete')

    name = 'complete'
    title = _(u'Completed')
    sortable = None
    insert_after = '*'

    def __init__(self, context):
        self.context = context

    def filterable(self):
        """ Returns a vocabulary for filtering the column or None if no filtering is available
        """
        return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(0, 'no', _p(u'No')), vocabulary.SimpleTerm(1, 'yes', _p(u'Yes'))])

    def factory(self, object, request):
        """ Returns the value to be displayed for the given object
        """
        return IComplete(object, lambda: False)() and _p(u'Yes') or _p(u'No')

    def cache_key(self, key, *args, **kwargs):
        """ Modifies the cache key if needed and returns it
        """
        return key + parents_modification_cache_key(self.context)


class OfferColumnProvider(grok.Adapter):
    """ Column provider adding the offer column
    """
    grok.implements(interfaces.IColumnProvider)
    grok.context(interface.Interface)
    grok.name('horae.search.column.offer')

    name = 'offer'
    title = _(u'Offer')
    sortable = None
    insert_after = '*'

    def __init__(self, context):
        self.context = context

    def filterable(self):
        """ Returns a vocabulary for filtering the column or None if no filtering is available
        """
        return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(0, 'no', _p(u'No')), vocabulary.SimpleTerm(1, 'yes', _p(u'Yes'))])

    def factory(self, object, request):
        """ Returns the value to be displayed for the given object
        """
        return IOffer(object, lambda: False)() and _p(u'Yes') or _p(u'No')

    def cache_key(self, key, *args, **kwargs):
        """ Modifies the cache key if needed and returns it
        """
        return key + parents_modification_cache_key(self.context)
