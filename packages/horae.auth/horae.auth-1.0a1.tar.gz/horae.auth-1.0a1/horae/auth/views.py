import grok
from operator import itemgetter

from zope import interface
from zope import component
from zope.event import notify
from zope.formlib.widget import renderElement
from zope.authentication.interfaces import IAuthentication, IUnauthenticatedPrincipal, ILogout
from zope.securitypolicy.interfaces import IPrincipalRoleManager, Allow, IRole
from megrok import navigation

from horae.layout import layout
from horae.layout.interfaces import IContextualManageMenu

from horae.auth import _
from horae.auth import interfaces
from horae.auth import utils
from horae.auth.events import SharingModifiedEvent

grok.templatedir('templates')


class Login(layout.Form):
    """ A form providing fields to login using the schema defined by
        :py:class:`horae.auth.interfaces.ILoginForm`
    """
    grok.context(interface.Interface)
    grok.require('zope.Public')
    grok.template('login')

    label = _(u'Login')
    form_fields = grok.AutoFields(interfaces.ILoginForm)

    def __call__(self):
        self.additional = renderElement('input',
                                        type='hidden',
                                        name='camefrom',
                                        value=self.request.form.get('camefrom', ''))
        return super(Login, self).__call__()

    @grok.action(_('login'))
    def login(self, **data):
        redirect = self.request.form.get('camefrom', '')
        if (not redirect or
            redirect == self.url(self.context) or
            redirect == self.url(self.context, 'index') or
            redirect == self.url(self.context, '@@index')):
            redirect = interfaces.IStartPage(self.request, lambda: redirect)()
        self.redirect(redirect)


class Logout(layout.View):
    """ A view to log out a user
    """
    grok.context(interface.Interface)
    grok.require('zope.Public')
    grok.template('logout')

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
        self.redirect(self.url(self.context))


class Sharing(layout.View):
    """ A view to define permissions on a given context implementing
        :py:class:`horae.auth.interfaces.IShareable`
    """
    grok.context(interfaces.IShareable)
    grok.require('horae.Sharing')
    navigation.menuitem(IContextualManageMenu, _(u'Sharing'))

    def update(self):
        super(Sharing, self).update()
        self.manager = IPrincipalRoleManager(self.context)

        providers = component.getAllUtilitiesRegisteredFor(interface=interfaces.ISelectableRoleProvider)
        roles = set()
        for provider in providers:
            roles.update(provider.roles())
        self.roles = [component.queryUtility(IRole, name=role) for role in roles]

        if self.request.form.get('update_sharing', None) is not None:
            self.save()

        self.authentication = component.getUtility(IAuthentication)
        self.principals = {}
        for role in self.roles:
            principals = dict(self.manager.getPrincipalsForRole(role.id, False))
            for id, setting in self.manager.getPrincipalsForRole(role.id):
                if setting is not Allow:
                    continue
                if not id in self.principals:
                    principal = self.authentication.getPrincipal(id)
                    self.principals[id] = {'id': principal.id,
                                           'name': principal.title,
                                           'group': utils.getGroup(id) is not None,
                                           'roles': [],
                                           'inherited': []}
                if principals.get(id, None) is Allow:
                    self.principals[id]['roles'].append(role.id)
                else:
                    self.principals[id]['inherited'].append(role.id)

        if self.request.form.get('search_principal', None) is not None:
            self.search(self.request.form.get('search_term', ''))

        self.principals = sorted(self.principals.values(), key=itemgetter('name'))

    def search(self, search_term):
        users = utils.getUsers()
        for user in users:
            if not user.username in self.principals and (search_term in user.username or search_term in user.name):
                self.principals[user.username] = {'id': user.username,
                                                  'name': user.name,
                                                  'group': False,
                                                  'roles': [],
                                                  'inherited': []}
        groups = utils.getGroups()
        for group in groups:
            if not group.id in self.principals and (search_term in group.id or search_term in group.name):
                self.principals[group.id] = {'id': group.id,
                                             'name': group.name,
                                             'group': True,
                                             'roles': [],
                                             'inherited': []}

    def save(self):
        self.manager.inherit = self.request.form.get('inherit', False)
        principals = self.request.form.get('principals', [])
        for principal in principals:
            for role in self.roles:
                if principal in self.request.form.get(role.id, []):
                    self.manager.assignRoleToPrincipal(role.id, principal)
                else:
                    self.manager.unsetRoleForPrincipal(role.id, principal)
        notify(SharingModifiedEvent(self.context))
        self.flash(_(u'Permissions successfully updated'), u'success')
