import grok

from zope import schema
from zope import component
from zope import interface
from zope.i18n import translate
from zope.catalog.field import FieldIndex
from zope.catalog.text import TextIndex
from zope.catalog.interfaces import ICatalog
from zope.publisher.interfaces.browser import IBrowserRequest
from zc.catalog.catalogindex import SetIndex

from hurry import query

from horae.core import utils
from horae.properties.properties import Property
from horae.properties.interfaces import IBoolProperty, \
    IDateTimeRangeProperty, IDateTimeProperty, IGroupProperty, IUserProperty, \
    IFloatProperty, IChoiceProperty, IRichTextProperty, ITextProperty, ITextLineProperty, \
    IWeightedChoiceProperty, IPropertied
from horae.autocomplete import fields
from horae.autocomplete.interfaces import IAutocompleteList, IValueProvider, IFieldProvider
from horae.autocomplete.providers import AbstractContextValueProvider

from horae.search import _
from horae.search.utils import normalizeDatetime
from horae.search import interfaces


class IKeywordAutocompleteList(IAutocompleteList):
    """ Marker interface for keyword autocomplete field
    """


class KeywordAutocompleteList(fields.AutocompleteList):
    """ Keyword autocomplete field
    """
    grok.implements(IKeywordAutocompleteList)


class KeywordValueProvider(grok.MultiAdapter, AbstractContextValueProvider):
    """ Value provider for keyword autocomplete fields getting
        the available values from the catalog and adding an
        additional one using the term entered
    """
    grok.adapts(interface.Interface, IKeywordAutocompleteList, IBrowserRequest)
    grok.provides(IValueProvider)

    def __call__(self, term):
        catalog = component.getUtility(ICatalog, 'properties')
        values = []
        if self.field.__name__ in catalog:
            values = self._searchVocabulary(term, schema.vocabulary.SimpleVocabulary.fromValues(catalog[self.field.__name__].values()))
        if not (term, term) in values:
            values.insert(0, (term, term))
        return values


class KeywordFieldProvider(grok.MultiAdapter):
    """ Field provider getting the field from the available
        properties
    """
    grok.adapts(IPropertied, IBrowserRequest)
    grok.provides(IFieldProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, name):
        property = self.context.find_property(name)
        if property is None:
            return None
        return property.fields(self.context).pop(0)


class KeywordProperty(Property):
    """ A keyword property
    """
    grok.implements(interfaces.IKeywordProperty)
    type = _(u'Keyword')
    default = schema.fieldproperty.FieldProperty(interfaces.IKeywordProperty['default'])

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            KeywordAutocompleteList(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                default=self.default,
                value_type=schema.TextLine()
            ),
        ])

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if value is None:
            return value
        return ', '.join(value)

    def empty(self, value):
        """ Decides whether the value provided is an empty value for this property type
        """
        try:
            return value is None or not len(value)
        except:
            return True


class BaseSearchableProperty(grok.Adapter):
    """ Base implementation of a searchable property
    """
    grok.baseclass()
    grok.implements(interfaces.ISearchableProperty)

    index_class = FieldIndex
    search_field = schema.TextLine

    def indexes(self):
        """ Returns a list of indexes required for this property
        """
        return [self.index_class(field_name=self.context.id), ]

    def index(self, value, field, context):
        """ Processes the value before indexing
        """
        return value

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([self.search_field(
            __name__=self.context.id,
            title=self.context.name,
            required=False,
        ), ])

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.context.id, ]

    def query(self, **data):
        """ Returns a query
        """
        if not self.context.id in data or data[self.context.id] is None:
            return None
        return query.Eq(('properties', self.context.id), data[self.context.id])

    def update(self, view):
        """ Called after all fields are set
        """
        pass


class BaseSearchableTextProperty(BaseSearchableProperty):
    """ Base implementation of a searchable text property
    """
    grok.baseclass()

    index_class = TextIndex

    def query(self, **data):
        """ Returns a list of queries
        """
        if not self.context.id in data or data[self.context.id] is None:
            return None
        return query.Text(('properties', self.context.id), '*' + '* *'.join(data[self.context.id].split(' ')) + '*')


class SearchableBoolProperty(BaseSearchableProperty):
    """ Searchable boolean property
    """
    grok.context(IBoolProperty)

    search_field = schema.Bool


class SearchableTextLineProperty(BaseSearchableTextProperty):
    """ Searchable text line property
    """
    grok.context(ITextLineProperty)


class SearchableTextProperty(BaseSearchableTextProperty):
    """ Searchable text property
    """
    grok.context(ITextProperty)


class SearchableRichTextProperty(BaseSearchableTextProperty):
    """ Searchable rich text property
    """
    grok.context(IRichTextProperty)


class BaseSearchableChoiceProperty(BaseSearchableProperty):
    """ Base implementation of a searchable choice property
    """
    grok.baseclass()

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([fields.AutocompleteList(
            __name__=self.context.id,
            title=self.context.name,
            description=self.context.description,
            value_type=schema.Choice(
                vocabulary=self.context.getVocabulary(context),
            ),
            required=False,
        ), ])

    def query(self, **data):
        """ Returns a query
        """
        if not self.context.id in data or data[self.context.id] is None:
            return None
        return query.In(('properties', self.context.id), data[self.context.id])


class SearchableChoiceProperty(BaseSearchableChoiceProperty):
    """ Searchable choice property
    """
    grok.context(IChoiceProperty)


class SearchableWeightedChoiceProperty(BaseSearchableChoiceProperty):
    """ Searchable weighted choice property
    """
    grok.context(IWeightedChoiceProperty)


class SearchableFloatProperty(BaseSearchableProperty):
    """ Searchable float property
    """
    grok.context(IFloatProperty)

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([schema.Float(
            __name__=self.context.id + '_min',
            title='%s (%s)' % (translate(self.context.name, context=request), translate(_(u'Min'), context=request)),
            description=self.context.description,
            min=self.context.min,
            max=self.context.max,
            required=False,
        ),
        schema.Float(
            __name__=self.context.id + '_max',
            title='%s (%s)' % (translate(self.context.name, context=request), translate(_(u'Max'), context=request)),
            min=self.context.min,
            max=self.context.max,
            required=False,
        ), ])

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.context.id + '_min', self.context.id + '_max', ]

    def query(self, **data):
        """ Returns a query
        """
        queries = []
        if self.context.id + '_min' in data and data[self.context.id + '_min'] is not None:
            queries.append(query.Ge(('properties', self.context.id), data[self.context.id + '_min']))
        if self.context.id + '_max' in data and data[self.context.id + '_max'] is not None:
            queries.append(query.Le(('properties', self.context.id), data[self.context.id + '_max']))
        if len(queries) == 1:
            return queries[0]
        elif len(queries) > 1:
            return query.And(*queries)
        return None


class SearchableKeywordProperty(BaseSearchableProperty):
    """ Searchable keyword property
    """
    grok.context(interfaces.IKeywordProperty)

    index_class = SetIndex

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        vocabulary = schema.vocabulary.SimpleVocabulary.fromValues(catalog[self.context.id].values())
        if not len(vocabulary):
            return []
        return self.context._prepare_fields([fields.AutocompleteList(
            __name__=self.context.id,
            title=self.context.name,
            description=self.context.description,
            value_type=schema.Choice(
                vocabulary=vocabulary
            ),
            required=False,
        ), ])

    def query(self, **data):
        """ Returns a query
        """
        if not self.context.id in data or data[self.context.id] is None:
            return None
        return query.set.AnyOf(('properties', self.context.id), data[self.context.id])


class SearchableUserProperty(SearchableChoiceProperty):
    """ Searchable user property
    """
    grok.context(IUserProperty)

    vocabulary = 'horae.auth.vocabulary.usernamesandme'

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([fields.AutocompleteList(
            __name__=self.context.id,
            title=self.context.name,
            description=self.context.description,
            value_type=schema.Choice(
                vocabulary=self.vocabulary
            ),
            required=False,
        ), ])

    def query(self, **data):
        """ Returns a query
        """
        value = data.get(self.context.id, None)
        if value is not None and u'me' in value:
            try:
                data[self.context.id][value.index(u'me')] = utils.getRequest().principal.id
            except:
                pass
        return super(SearchableUserProperty, self).query(**data)


class SearchableGroupProperty(SearchableUserProperty):
    """ Searchable group property
    """
    grok.context(IGroupProperty)

    vocabulary = 'horae.auth.vocabulary.groupids'


class SearchableDateTimeProperty(BaseSearchableProperty):
    """ Searchable date time property
    """
    grok.context(IDateTimeProperty)

    def index(self, value, field, context):
        """ Processes the value before indexing
        """
        return normalizeDatetime(value)

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([schema.Datetime(
            __name__=self.context.id + '_min',
            title='%s (%s)' % (translate(self.context.name, context=request), translate(_(u'Min'), context=request)),
            description=self.context.description,
            required=False,
        ),
        schema.Datetime(
            __name__=self.context.id + '_max',
            title='%s (%s)' % (translate(self.context.name, context=request), translate(_(u'Max'), context=request)),
            description=self.context.description,
            required=False,
        ), ])

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.context.id + '_min', self.context.id + '_max', ]

    def query(self, **data):
        """ Returns a query
        """
        queries = []
        if self.context.id + '_min' in data and data[self.context.id + '_min'] is not None:
            queries.append(query.Ge(('properties', self.context.id), normalizeDatetime(data[self.context.id + '_min'])))
        if self.context.id + '_max' in data and data[self.context.id + '_max'] is not None:
            queries.append(query.Le(('properties', self.context.id), normalizeDatetime(data[self.context.id + '_max'])))
        if len(queries) == 1:
            return queries[0]
        elif len(queries) > 1:
            return query.And(*queries)
        return None


class SearchableDateTimeRangeProperty(SearchableDateTimeProperty):
    """ Searchable date time range property
    """
    grok.context(IDateTimeRangeProperty)

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        return self.context._prepare_fields([schema.Datetime(
            __name__=self.context.id + '_min',
            title='%s (%s)' % (translate(self.context.name_end, context=request), translate(_(u'Min'), context=request)),
            description=self.context.description,
            required=False,
        ),
        schema.Datetime(
            __name__=self.context.id + '_max',
            title='%s (%s)' % (translate(self.context.name, context=request), translate(_(u'Max'), context=request)),
            description=self.context.description,
            required=False,
        ), ])

    def field_names(self):
        """ Returns a list of field names provided by this property
        """
        return [self.context.id + '_min', self.context.id + '_max', ]

    def indexes(self):
        """ Returns a list of indexes required for this property
        """
        return [self.index_class(field_name=self.context.id + '_start'), self.index_class(field_name=self.context.id + '_end'), ]

    def query(self, **data):
        """ Returns a query
        """
        queries = []
        if self.context.id + '_min' in data and data[self.context.id + '_min'] is not None:
            queries.append(query.Ge(('properties', self.context.id + '_end'), normalizeDatetime(data[self.context.id + '_min'])))
        if self.context.id + '_max' in data and data[self.context.id + '_max'] is not None:
            queries.append(query.Le(('properties', self.context.id + '_start'), normalizeDatetime(data[self.context.id + '_max'])))
        if len(queries) == 1:
            return queries[0]
        elif len(queries) > 1:
            return query.And(*queries)
        return None
