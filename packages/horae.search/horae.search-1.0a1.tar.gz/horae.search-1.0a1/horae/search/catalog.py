import grok

from grok import index
from zope import interface
from zope import component
from zope.location.interfaces import ILocationInfo
from zope.catalog.interfaces import ICatalog
from zope.securitypolicy.rolepermission import rolePermissionManager
from zope.securitypolicy.principalpermission import principalPermissionManager
from zope.securitypolicy.principalrole import principalRoleManager
from zope.securitypolicy.interfaces import Allow, IRolePermissionMap, IPrincipalPermissionMap, IPrincipalRoleMap
from zope.security.interfaces import IGroupAwarePrincipal
from zope.site.hooks import getSite
from zope.intid.interfaces import IIntIds

from hurry.query.interfaces import IQuery
from hurry.query.query import Query as BaseQuery
from hurry.query import set

from horae.core import utils
from horae.core.interfaces import IHorae
from horae.properties.interfaces import IPropertied, IProperty, IDefaultProperty, IWeightedChoiceProperty, IComplete, IOffer
from horae.lifecycle.interfaces import ILifecycleAware
from horae.ticketing import interfaces
from horae.ticketing import ticketing
from horae.auth.interfaces import ISharingModifiedEvent

from horae.search.utils import normalizeDatetime
from horae.search.interfaces import ISearchable, ISearchablePropertied, ISearchableProperty, ISortingProvider

ALLOWED_PERMISSION = 'horae.View'


class Query(BaseQuery):
    """ Query implementation which additionally filters the search result
        based on the permissions of the current user
    """

    def _allowed(self):
        try:
            request = utils.getRequest()
        except:
            return []
        principal = request.principal
        allowed = ['principal:' + principal.id, ]
        if IGroupAwarePrincipal.providedBy(principal):
            for group in principal.groups:
                allowed.append('principal:' + group)
        roles = IPrincipalRoleMap(getSite()).getRolesForPrincipal(principal.id) + principalRoleManager.getRolesForPrincipal(principal.id)
        for role, setting in roles:
            try:
                if setting is Allow:
                    allowed.append('role:' + role)
            except TypeError:
                pass
        return allowed

    def searchResults(self, query, unrestricted=False, **kw):
        if not unrestricted:
            query &= set.AnyOf(('catalog', 'allowed'), self._allowed())
        return super(Query, self).searchResults(query, **kw)


class Indexes(grok.Indexes):
    """ Defines the indexes of the catalog
    """
    grok.site(IHorae)
    grok.context(ISearchable)
    grok.name('catalog')

    id = index.Field()
    implements = index.Set()
    type = index.Field()
    sortable_name = index.Field()
    text = index.Text()
    creator = index.Field()
    creation_date = index.Value()
    modifier = index.Field()
    modification_date = index.Value()
    path = index.Set()
    milestone = index.Field()
    project = index.Field()
    client = index.Field()
    allowed = index.Set()
    sorting = index.Value()
    complete = index.Field()
    offer = index.Field()


class Searchable(grok.Adapter):
    """ Base implementation of a searchable object adapter
    """
    grok.baseclass()
    grok.implements(ISearchable)

    @property
    def id(self):
        return getattr(self.context, 'id', None)

    @property
    def implements(self):
        implements = []
        for iface in interface.providedBy(self.context):
            implements.append(iface.__identifier__)
            implements.extend([base.__identifier__ for base in iface.getBases()])
        return implements

    @property
    def type(self):
        if interfaces.IClient.providedBy(self.context):
            return 0
        if interfaces.IProject.providedBy(self.context):
            return 1
        if interfaces.IMilestone.providedBy(self.context):
            return 2
        if interfaces.ITicket.providedBy(self.context):
            return 3
        return 4

    @property
    def sortable_name(self):
        name = getattr(self.context, 'name', None)
        if name is None:
            return u''
        sortable_name = ''
        num = ''
        while len(name):
            char = name[0]
            name = name[1:]
            if char in '0123456789':
                num = '%s%s' % (num, char)
            if not char in '0123456789' or not len(name):
                if len(num):
                    if len(num) <= 10:
                        num = '%010d' % int(num)
                    sortable_name += num
                    num = ''
                if not char in '0123456789':
                    sortable_name += char
        return sortable_name

    @property
    def text(self):
        propertied = IPropertied(self.context, None)
        if propertied is None:
            return u''
        properties = propertied.properties()
        text = []
        for property in properties:
            for field in property.fields(propertied):
                value = propertied.get_property(field.__name__)
                if isinstance(value, basestring):
                    text.append(unicode(value))
        return u' '.join(text)

    @property
    def creator(self):
        if not ILifecycleAware.providedBy(self.context):
            return u''
        return self.context.creator is not None and self.context.creator or u''

    @property
    def creation_date(self):
        if not ILifecycleAware.providedBy(self.context):
            return u''
        return normalizeDatetime(self.context.creation_date)

    @property
    def modifier(self):
        if not ILifecycleAware.providedBy(self.context):
            return u''
        return self.context.modifier is not None and self.context.modifier or u''

    @property
    def modification_date(self):
        if not ILifecycleAware.providedBy(self.context):
            return u''
        return normalizeDatetime(self.context.modification_date)

    @property
    def path(self):
        info = ILocationInfo(self.context)
        path = [ILocationInfo(parent).getPath() for parent in info.getParents()]
        path.append(info.getPath())
        if interfaces.ITicket.providedBy(self.context) and self.context.milestone is not None:
            path.append(ILocationInfo(self.context.milestone).getPath())
        return path

    @property
    def milestone(self):
        if interfaces.ITicket.providedBy(self.context) and self.context.milestone is not None:
            return self.context.milestone.id
        return u'None'

    @property
    def project(self):
        if interfaces.ITicket.providedBy(self.context) or interfaces.IMilestone.providedBy(self.context):
            return utils.findParentByInterface(self.context, interfaces.IProject).id
        return u''

    @property
    def client(self):
        if interfaces.ITicket.providedBy(self.context) or interfaces.IMilestone.providedBy(self.context) or interfaces.IProject.providedBy(self.context):
            return utils.findParentByInterface(self.context, interfaces.IClient).id
        return u''

    @property
    def allowed(self):
        allowed = []
        roles = IRolePermissionMap(self.context).getRolesForPermission(ALLOWED_PERMISSION) + rolePermissionManager.getRolesForPermission(ALLOWED_PERMISSION)
        principals = IPrincipalPermissionMap(self.context).getPrincipalsForPermission(ALLOWED_PERMISSION) + principalPermissionManager.getPrincipalsForPermission(ALLOWED_PERMISSION)
        principal_role_map = IPrincipalRoleMap(self.context)
        for role, setting in roles:
            if setting is not Allow:
                continue
            allowed.append('role:' + role)
            principals.extend(principal_role_map.getPrincipalsForRole(role))
            principals.extend(principalRoleManager.getPrincipalsForRole(role))
        for principal, setting in principals:
            if setting is Allow:
                allowed.append('principal:' + principal)
        return allowed

    @property
    def sorting(self):
        sorting = 0
        providers = [provider for name, provider in component.getAdapters((self.context,), ISortingProvider)]
        for provider in providers:
            sorting += provider.add()
        for provider in providers:
            sorting = provider.adjust(sorting)
        return sorting

    @property
    def complete(self):
        return 1 if IComplete(self.context, lambda: False)() else 0

    @property
    def offer(self):
        return 1 if IOffer(self.context, lambda: False)() else 0


class SearchableClient(Searchable):
    """ Searchable client
    """
    grok.context(ticketing.Client)


class SearchableProject(Searchable):
    """ Searchable project
    """
    grok.context(ticketing.Project)


class SearchableMilestone(Searchable):
    """ Searchable milestone
    """
    grok.context(ticketing.Milestone)


class SearchableTicket(Searchable):
    """ Searchable ticket
    """
    grok.context(ticketing.Ticket)


class WeightedChoiceSortingProvider(grok.Adapter):
    """ Sorting provider for weighted choice properties
    """
    grok.implements(ISortingProvider)
    grok.context(IPropertied)

    def add(self):
        """ Returns the sum of the weight of all properties implementing
            :py:class:`horae.properties.interfaces.IWeightedChoiceProperty`
        """
        sorting = 0
        properties = self.context.properties()
        for property in properties:
            if not IWeightedChoiceProperty.providedBy(property) or not property.affects_sorting:
                continue
            value = self.context.get_property(property.id)
            for option in property.vocabulary:
                if option.name == value:
                    sorting += option.weight
                    break
        return sorting

    def adjust(self, sorting):
        return sorting


class PropertyIndexes(grok.Indexes):
    """ Provides indexes for the available properties
    """
    grok.site(IHorae)
    grok.context(ISearchablePropertied)
    grok.name('properties')


class SearchablePropertied(grok.Adapter):
    """ A searchable propertied object
    """
    grok.context(IPropertied)
    grok.implements(ISearchablePropertied)

    def __getattr__(self, name):
        propertied = IPropertied(self.context)
        request = utils.getRequest(None)
        for property in propertied.properties():
            if not property.searchable:
                continue
            indexer = ISearchableProperty(property, None)
            if indexer is None:
                continue
            if name in property.field_names():
                for field in property.fields(propertied):
                    if name == field.__name__:
                        return indexer.index(propertied.get_property(name, u''), field, self.context)
            catalog = component.getUtility(ICatalog, 'properties', self.context)
            if name in indexer.field_names():
                for field in indexer.fields(catalog, self.context, request):
                    if name == field.__name__:
                        return indexer.index(None, field, self.context)
        return u''


def createPropertyIndex(property, catalog=None):
    if not property.remember or not property.searchable:
        return []
    indexer = ISearchableProperty(property, None)
    if indexer is None:
        return []
    if catalog is None:
        catalog = component.getUtility(ICatalog, 'properties', property)
    created = []
    for index in indexer.indexes():
        if index.field_name in catalog and isinstance(catalog[index.field_name], index.__class__):
            if IDefaultProperty.providedBy(property):
                catalog[index.field_name].property_name = property.id
            else:
                catalog[index.field_name].property = property
            continue
        index.interface = ISearchablePropertied
        if IDefaultProperty.providedBy(property):
            index.property_name = property.id
        else:
            index.property = property
        catalog[index.field_name] = index
        catalog.updateIndex(catalog[index.field_name])
        created.append(index.field_name)
    return created


def createDefaultPropertyIndexes(horae):
    catalog = component.getUtility(ICatalog, 'properties', horae)
    properties = component.getAllUtilitiesRegisteredFor(IDefaultProperty)
    created = []
    for property in properties:
        created.extend(createPropertyIndex(property, catalog))
    return created


@grok.subscribe(IHorae, grok.IApplicationInitializedEvent)
def create_default_property_indexes(obj, event):
    """ Creates the indexes for all available default properties
        on application initialization
    """
    createDefaultPropertyIndexes(obj)


@grok.subscribe(IProperty, grok.IObjectModifiedEvent)
def create_property_index(obj, event):
    """ Creates or updates the index for the modified property
    """
    createPropertyIndex(obj)


@grok.subscribe(interface.Interface, ISharingModifiedEvent)
def reindex_object_security(obj, event):
    """ Reindexes an objects and all its childs security index
        after the permissions have been changed
    """
    catalog = component.getUtility(ICatalog, 'catalog')
    intid = component.getUtility(IIntIds, context=catalog)
    results = component.getUtility(IQuery).searchResults(set.AnyOf(('catalog', 'path'), [ILocationInfo(obj).getPath(), ]))
    index = catalog['allowed']
    for ob in results:
        index.index_doc(intid.queryId(ob), ob)
