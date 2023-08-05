from zope import component
from zope.catalog.interfaces import ICatalog

from plone.memoize import ram


def reindexSecurity():
    """ Updates the security index
    """
    catalog = component.queryUtility(ICatalog, 'catalog')
    if catalog is None:
        return
    catalog.updateIndex(catalog.get('allowed'))


@ram.cache(lambda method, *args, **kwargs: (method.__module__, method.__name__, args[0]))
def normalizeDatetime(dt):
    """ Normalizes a :py:class:`datetime.datetime` object to be used in an
        index
    """
    if dt is None:
        return None
    tmpin = dt.utctimetuple()[:5]
    multi = (535680, 44640, 1440, 60, 1) # Resolution in minutes
    value = sum(i * j for i, j in zip(tmpin, multi))
    return value
