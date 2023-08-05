from zope import interface
from zope import schema

from horae.core.interfaces import IIntId
from horae.lifecycle.interfaces import ILifecycleAware
from horae.ticketing import interfaces
from horae.properties.interfaces import ITextProperty
from horae.properties import _ as _p
from horae.autocomplete import fields

from horae.search import _


class ISearchable(IIntId, ILifecycleAware):
    """ Searchable object
    """

    sortable_name = interface.Attribute('sortable_name')
    type = interface.Attribute('type')
    implements = interface.Attribute('implements')
    text = interface.Attribute('text')
    path = interface.Attribute('path')
    milestone = interface.Attribute('milestone')
    project = interface.Attribute('project')
    client = interface.Attribute('client')
    allowed = interface.Attribute('allowed')
    sorting = interface.Attribute('sorting')
    complete = interface.Attribute('complete')
    offer = interface.Attribute('offer')


class ISearchablePropertied(interface.Interface):
    """ A searchable propertied object
    """


class IKeywordProperty(ITextProperty):
    """ A keyword property
    """


class ISearchableProperty(interface.Interface):
    """ A searchable property
    """

    def indexes():
        """ Returns a list of indexes required for this property
        """

    def index(value, field, context):
        """ Processes the value before indexing
        """

    def fields(catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """

    def field_names():
        """ Returns a list of field names provided by this property
        """

    def query(**data):
        """ Returns a query
        """

    def update(view):
        """ Called after all fields are set
        """


class ISearchForm(interface.Interface):
    """ The search form
    """

    text = schema.TextLine(
        title=_(u'Full text'),
        required=False
    )

    implements = schema.Set(
        title=_(u'Search for'),
        required=False,
        value_type=schema.Choice(
            vocabulary=schema.vocabulary.SimpleVocabulary((
                schema.vocabulary.SimpleTerm(interfaces.IClient.__identifier__, interfaces.IClient.__identifier__, _(u'Clients')),
                schema.vocabulary.SimpleTerm(interfaces.IProject.__identifier__, interfaces.IProject.__identifier__, _(u'Projects')),
                schema.vocabulary.SimpleTerm(interfaces.IMilestone.__identifier__, interfaces.IMilestone.__identifier__, _(u'Milestones')),
                schema.vocabulary.SimpleTerm(interfaces.ITicket.__identifier__, interfaces.ITicket.__identifier__, _(u'Tickets'))
            ))
        ),
        default=set([interfaces.IClient.__identifier__,
                     interfaces.IProject.__identifier__,
                     interfaces.IMilestone.__identifier__,
                     interfaces.ITicket.__identifier__, ])
    )

    current = schema.Bool(
        title=_(u'Only in current context'),
        required=False
    )


class IAdvancedSearchForm(ISearchForm):
    """ The advanced search form
    """

    complete = schema.Choice(
        title=_(u'Completed'),
        required=False,
        vocabulary=schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(0, 'no', _p(u'No')), schema.vocabulary.SimpleTerm(1, 'yes', _p(u'Yes'))])
    )

    offer = schema.Choice(
        title=_(u'Offer'),
        required=False,
        vocabulary=schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(0, 'no', _p(u'No')), schema.vocabulary.SimpleTerm(1, 'yes', _p(u'Yes'))])
    )

    client = fields.AutocompleteList(
        title=_(u'Clients'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.search.vocabulary.clients'
        )
    )

    project = fields.AutocompleteList(
        title=_(u'Projects'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.search.vocabulary.projects'
        )
    )

    milestone = fields.AutocompleteList(
        title=_(u'Milestones'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.search.vocabulary.milestones'
        )
    )


class IAdvancedSearchFieldProvider(interface.Interface):
    """ A provider of fields added to the advanced search form
    """

    def fields():
        """ Returns a list of fields to be added to the form
        """

    def query(**data):
        """ Returns a list of queries
        """


class ISortingProvider(interface.Interface):
    """ A provider for adjusting the sorting of tickets
    """

    def add():
        """ Returns an integer to be added to the sorting
        """

    def adjust(sorting):
        """ Adjusts the sorting after all providers sorting where added and returns the adjusted sorting
        """


class IDefaultSortingProvider(interface.Interface):
    """ A provider defining the default sorting
    """

    def sort_field():
        """ The index used to sort
        """

    def reverse():
        """ Whether to reverse the sort order
        """


class IRowClassProvider(interface.Interface):
    """ A provider for CSS classes set on search result rows
    """

    def classes():
        """ Returns a list of CSS classes to be set on the row
        """


class IColumnProvider(interface.Interface):
    """ A provider for a table column
    """

    name = interface.Attribute('name')
    title = interface.Attribute('title')
    sortable = interface.Attribute('sortable')
    insert_after = interface.Attribute('insert_after')

    def filterable():
        """ Returns a vocabulary for filtering the column or None if no filtering is available
        """

    def factory(object, request):
        """ Returns the value to be displayed for the given object
        """

    def cache_key(key, *args, **kwargs):
        """ Modifies the cache key if needed and returns it
        """
