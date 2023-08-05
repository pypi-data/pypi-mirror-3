from zope import component
from zope.security.management import checkPermission, getSecurityPolicy
from zope.pluggableauth.factories import Principal
from zope.site.hooks import getSite

from horae.auth import interfaces


def getUsers():
    """ Returns a list of the available :py:class:`horae.auth.interfaces.IUser` provided by all registered
        :py:class:`horae.auth.interfaces.IUserProvider`
    """
    providers = component.getAllUtilitiesRegisteredFor(interfaces.IUserProvider)
    users = []
    for provider in providers:
        users.extend(provider.users())
    return users


def getUser(username):
    """ Returns the :py:class:`horae.auth.interfaces.IUser` having the provided username
        or None if no matching user was found
    """
    providers = component.getAllUtilitiesRegisteredFor(interfaces.IUserProvider)
    for provider in providers:
        user = provider.get_user(username)
        if user is not None:
            return user
    return None


def displayUser(username):
    """ Returns a string to be used to display the user having the provided username

        * If the user does not exist, the username is returned
        * If the user exists, its name is returned
        * If additionally an adapter providing :py:class:`horae.auth.interface.IUserURL`
          is found the users name is surrounded by an HTML link pointing to the URL provided
          by the adapter
    """
    user = getUser(username)
    url = user is not None and interfaces.IUserURL(user) or None
    return user is not None and (url is not None and '<a href="%s">%s</a>' % (url(), user.name) or user.name) or username


def getGroups():
    """ Returns a list of the available :py:class:`horae.auth.interfaces.IGroup` provided by all registered
        :py:class:`horae.auth.interfaces.IGroupProvider`
    """
    providers = component.getAllUtilitiesRegisteredFor(interfaces.IGroupProvider)
    groups = []
    for provider in providers:
        groups.extend(provider.groups())
    return groups


def getGroup(groupid):
    """ Returns the :py:class:`horae.auth.interfaces.IGroup` having the provided ID
        or None if no matching group was found
    """
    providers = component.getAllUtilitiesRegisteredFor(interfaces.IGroupProvider)
    for provider in providers:
        group = provider.get_group(groupid)
        if group is not None:
            return group
    return None


class Participant(object):
    interaction = None
    principal = None


def checkPermissionForPrincipal(permission, object, principal_id):
    """ Checks whether the principal having the given ID has the permission
        in the context. Where principal_id may either be the username of a
        :py:class:`horae.auth.interfaces.IUser` or the ID of a
        :py:class:`horae.auth.interfaces.IGroup`
    """
    participant = Participant()
    user = getUser(principal_id)
    if user is None:
        group = getGroup(principal_id)
        if group is None:
            return False
        participant.principal = Principal(group.id, group.name)
    else:
        participant.principal = Principal(user.username, user.name)
        participant.principal.groups.extend([group.id for group in user.groups])
    interaction = getSecurityPolicy()()
    interaction.add(participant)
    return checkPermission(permission, object, interaction)
