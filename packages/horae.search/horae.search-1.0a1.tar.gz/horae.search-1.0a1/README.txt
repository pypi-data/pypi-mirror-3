Introduction
============

The ``horae.search`` provides searching functionality for the Horae
resource planning system by implementing a ajax driven full text search
and a pluggable advanced search form. Additionally it implements a
restricted special ``Query`` implementation based on the one provided
by `hurry.query <http://pypi.python.org/pypi/hurry.query>`_ which only
returns results the user is allowed to see.

Usage
=====

There are several ways to extend and adjust the behaviour of the search
forms and results by registering special adapters. The following possibilities
are available for any views sub-classing from ``horae.search.search.SearchMixin``.

Extending the advanced search form
----------------------------------

The advanced search form may be extended by registering a named multi adapter
implementing ``horae.search.interfaces.IAdvancedSearchFieldProvider``
and adapting the ``context`` and ``request``. If for example one would
like to add a new ``TextLine`` field searching in a custom catalog the
implementation would look something like this::

    import grok
    
    from zope import interface
    from zope import schema
    from zope.publisher.interfaces.browser import IBrowserRequest
    
    from hurry import query
    
    from horae.search import interfaces
    
    class SampleAdvancedSearchFieldProvider(grok.MultiAdapter):
        grok.adapts(interface.Interface, IBrowserRequest)
        grok.implements(interfaces.IAdvancedSearchFieldProvider)
        grok.name('sampleadvancedfieldprovider')
    
        def __init__(self, context, request):
            self.context = context
            self.request = request
    
        def fields(self):
            """ Returns a list of fields to be added to the form
            """
            return [
                schema.TextLine(
                    __name__ = 'sample_text_line',
                    title = u'Sample text line'
                )
            ]
    
        def query(self, **data):
            """ Returns a list of queries
            """
            queries = []
            if 'sample_text_line' in data:
                queries.append(query.Text(('samplecatalog', 'text'),
                                          data['sample_text_line']))
            return queries

Adjusting default sorting
-------------------------

By default the search results are sorted by a special integer index in the catalog.
This integer may be adjusted by registering a named adapter implementing
``horae.search.interfaces.ISortingProvider`` and adapting the object the sorting
should be changed for. If for example one would like to move every ticket having
a special property set to the bottom of the search results the implementation
would look like this::

    from horae.ticketing.interfaces import ITicket
    
    class SampleSortingProvider(grok.Adapter):
        grok.context(ITicket)
        grok.implements(interfaces.ISortingProvider)
        grok.name('samplesortingprovider')
    
        def add(self):
            """ Returns an integer to be added to the sorting
            """
            return 0
    
        def adjust(self, sorting):
            """ Adjusts the sorting after all providers sorting
                where added and returns the adjusted sorting
            """
            if (self.context.get_property('my_special_property', None) is not None):
                return 0
            return sorting

Changing default sorting
------------------------

As mentioned above the default sorting of the search results is a special integer index
in the catalog. This may be changed by registering an adapter implementing
``horae.search.interfaces.IDefaultSortingProvider`` and adapting either the
search view or the search view and the desired context. An example implementation
changing the default sorting of the advanced search results would look like this::

    from horae.search import search
    
    class SampleDefaultSortingProvider(grok.Adapter):
        grok.context(search.AdvancedSearch)
        grok.implements(interfaces.IDefaultSortingProvider)
    
        def sort_field(self):
            """ The index used to sort
            """
            return ('samplecatalog', 'sorting')
    
        def reverse(self):
            """ Whether to reverse the sort order
            """
            return False

Adding columns
--------------

Adding new columns to the results table is possible by registering a named adapter
implementing ``horae.search.interfaces.IColumnProvider`` adapting the desired ``context``.
The following is an example implementation found in ``horae.search.search`` providing
a column showing whether an object has been completed or not::

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
            """ Returns a vocabulary for filtering the column or
                None if no filtering is available
            """
            return vocabulary.SimpleVocabulary([
                vocabulary.SimpleTerm(0, 'no', _p(u'No')),
                vocabulary.SimpleTerm(1, 'yes', _p(u'Yes'))
            ])
    
        def factory(self, object, request):
            """ Returns the value to be displayed for the given object
            """
            return (IComplete(object, lambda: False)() and _p(u'Yes') or _p(u'No'))
    
        def cache_key(self, key, *args, **kwargs):
            """ Modifies the cache key if needed and returns it
            """
            return key + parents_modification_cache_key(self.context)

Adding row CSS class
--------------------

Last but not least one may add custom CSS classes to the rows by registering
a named adapter implementing ``horae.search.interfaces.IRowClassProvider``
adapting the desired ``context``. An example implementation adding a CSS class
``special`` if a ticket has a special property set would look like this::

    class SampleRowClassProvider(grok.Adapter):
        grok.context(ITicket)
        grok.implements(interfaces.IRowClassProvider)
    
        def classes(self):
            """ Returns a list of CSS classes to be set on the row
            """
            if (self.context.get_property('my_special_property', None) is not None):
                return ['special']
            return []

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.autocomplete <http://pypi.python.org/pypi/horae.autocomplete>`_
* `horae.cache <http://pypi.python.org/pypi/horae.cache>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.lifecycle <http://pypi.python.org/pypi/horae.lifecycle>`_
* `horae.properties <http://pypi.python.org/pypi/horae.properties>`_
* `horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `zc.catalog <http://pypi.python.org/pypi/zc.catalog>`_
* `hurry.query <http://pypi.python.org/pypi/hurry.query>`_
