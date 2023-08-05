from zope import component
from zope.annotation import IAnnotations
from zope.securitypolicy.interfaces import Unset, Deny
from zope.securitypolicy.principalrole import AnnotationPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from plone.memoize import forever, instance

from horae.auth.utils import getUsers, getGroups
from horae.auth.interfaces import ISelectableRoleProvider

FORCE_INHERIT_ROLES = ['zope.Manager', 'horae.Manager', 'horae.Administrator']


class InheritingManagerMixin:
    inherit_key = 'horae.auth.inherit'
    iface = None

    def __nonzero__(self):
        return True

    def get_inherit(self):
        return IAnnotations(self._context).get(self.inherit_key, True)

    def set_inherit(self, value):
        IAnnotations(self._context)[self.inherit_key] = value
    inherit = property(get_inherit, set_inherit)

    @property
    @forever.memoize
    def selectable_roles(self):
        providers = component.getAllUtilitiesRegisteredFor(interface=ISelectableRoleProvider)
        roles = set()
        for provider in providers:
            roles.update(provider.roles())
        return roles

    def check_inherit(self, inherited, role_id=None):
        if not inherited or self.parent is None:
            return False
        if role_id is not None and not role_id in self.selectable_roles:
            return True
        return self.inherit

    @property
    @instance.memoize
    def parent(self):
        if getattr(self._context, '__parent__', None) is None:
            return None
        return self.iface(self._context.__parent__)


class InheritingAnnotationPrincipalRoleManager(InheritingManagerMixin, AnnotationPrincipalRoleManager):
    """ A Custom :py:class:`zope.securitypolicy.interfaces.IPrincipalRoleManager`
        for objects implementing :py:class:`horae.auth.interfaces.IShareable`
        providing disabling of role inheritance
    """
    iface = IPrincipalRoleManager

    def getPrincipalsForRole(self, role_id, inherited=True):
        principals = {}
        if self.check_inherit(inherited, role_id):
            principals.update(dict(self.parent.getPrincipalsForRole(role_id)))
        elif not self.inherit and role_id in self.selectable_roles:
            for user in getUsers():
                if not user.username in principals:
                    principals[user.username] = Deny
            for group in getGroups():
                if not group.id in principals:
                    principals[group.id] = Deny
        principals.update(dict(super(InheritingAnnotationPrincipalRoleManager, self).getPrincipalsForRole(role_id)))
        return principals.items()

    def getRolesForPrincipal(self, principal_id, inherited=True):
        roles = {}
        if self.parent is not None:
            selectable = self.selectable_roles
            inherited = self.parent.getRolesForPrincipal(principal_id)
            for role, setting in inherited:
                if self.inherit or not role in selectable:
                    roles[role] = setting
        roles.update(dict(super(InheritingAnnotationPrincipalRoleManager, self).getRolesForPrincipal(principal_id)))
        if not self.inherit:
            providers = component.getAllUtilitiesRegisteredFor(interface=ISelectableRoleProvider)
            for provider in providers:
                for role in provider.roles():
                    if not role in roles:
                        roles[role] = Deny
        return roles.items()

    def getSetting(self, role_id, principal_id, default=Unset, inherited=True):
        setting = super(InheritingAnnotationPrincipalRoleManager, self).getSetting(role_id, principal_id, default)
        if setting is default:
            if self.check_inherit(inherited, role_id):
                setting = self.parent.getSetting(role_id, principal_id, default)
            elif not self.inherit:
                setting = Deny
        return setting

    def getPrincipalsAndRoles(self, inherited=True):
        principals_roles = super(InheritingAnnotationPrincipalRoleManager, self).getPrincipalsAndRoles()
        if self.check_inherit(inherited):
            principals_roles.extend(self.parent.getPrincipalsAndRoles())
        return principals_roles
