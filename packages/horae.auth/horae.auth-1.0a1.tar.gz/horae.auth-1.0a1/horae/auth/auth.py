import grok

from zope import component
from zope.site.hooks import getSite
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.pluggableauth.interfaces import ICredentialsPlugin, IAuthenticatorPlugin, AuthenticatedPrincipalCreated
from zope.pluggableauth.factories import PrincipalInfo
from zope.security.interfaces import IMemberGetterGroup
from zope.securitypolicy.interfaces import IPrincipalRoleManager, Allow
from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from horae.auth.utils import getUser, getGroup
from horae.auth import interfaces


def setup_authentication(pau):
    """Set up pluggable authentication utility.

    Sets up an :py:class:`zope.pluggableauth.interfaces.IAuthenticatorPlugin` and
    :py:class:`zope.pluggableauth.interfaces.ICredentialsPlugin` (for the authentication mechanism)
    """
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['users']


class SessionCredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    """ A credentials plugin using the login form provided by
        :py:class:`horae.auth.views.LoginForm`
    """
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.login'
    passwordfield = 'form.password'


class UserAuthenticatorPlugin(grok.GlobalUtility):
    """ An authenticator plugin using :py:class:`horae.auth.interfaces.IUserProvider`
        to find and authenticate users
    """
    grok.provides(IAuthenticatorPlugin)
    grok.name('users')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        user = self.getUser(credentials['login'])

        if user is None:
            return None
        if not user.checkPassword(credentials['password']):
            return None
        return PrincipalInfo(user.username, user.username, user.name, u'')

    def principalInfo(self, id):
        user = self.getUser(id)
        if user is not None:
            return PrincipalInfo(user.username, user.username, user.name, u'')
        group = self.getGroup(id)
        if group is not None:
            return PrincipalInfo(group.id, group.id, group.name, group.description)
        return None

    def getUser(self, id):
        return getUser(id)

    def getGroup(self, id):
        return getGroup(id)


class Group(object):
    grok.implements(IMemberGetterGroup)

    def __init__(self, id, title=u'', description=u''):
        self.id = id
        self.title = title
        self.description = description

    def getMembers(self):
        providers = component.getAllUtilitiesRegisteredFor(interfaces.IGroupProvider)
        catalog = component.getUtility(ICatalog)
        intids = component.getUtility(IIntIds)
        members = []
        for provider in providers:
            group = provider.get_group(self.id)
            if group is not None:
                try:
                    users = catalog.findRelations({'to_id': intids.getId(group)})
                except:
                    continue
                for user in users:
                    members.append(user.from_id)
        return members


@grok.adapter(interfaces.IGroup)
@grok.implementer(IMemberGetterGroup)
def members_getter_group_of_group(group):
    return Group(group.id, group.name, group.description)


@grok.subscribe(interfaces.IGroup, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.IUser, grok.IObjectModifiedEvent)
def update_principal_roles(user, event, principal=None, manager=None):
    if manager is None:
        manager = IPrincipalRoleManager(getSite())
    roles = list(user.roles if user.roles else [])
    if interfaces.IUser.providedBy(user):
        id = user.username
        roles.append(u'horae.Member')
        for group in user.groups:
            if group is None:
                continue
            if principal is not None:
                principal.groups.append(group.id)
            update_principal_roles(group, event, manager=manager)
    else:
        id = user.id
    existing = [role_id for role_id, value in manager.getRolesForPrincipal(id) if value is Allow]
    for role in roles:
        if not role in existing:
            manager.assignRoleToPrincipal(role, id)
    for role in existing:
        if not role in roles:
            manager.unsetRoleForPrincipal(role, id)


@grok.subscribe(AuthenticatedPrincipalCreated)
def authenticated_principal_created(event):
    user = getUser(event.principal.id)
    if user is None:
        user = getGroup(event.principal.id)
    if user is not None:
        update_principal_roles(user, event, event.principal)


class SelectableRoleProvider(grok.GlobalUtility):
    """ Provider for selectable roles
    """
    grok.implements(interfaces.ISelectableRoleProvider)
    grok.provides(interfaces.ISelectableRoleProvider)
    grok.name('horae.auth.selectableroles')

    def roles(self):
        """ Returns a list of role names
        """
        return ['horae.Reader', 'horae.Editor', 'horae.Contributor', 'horae.TicketEditor']
