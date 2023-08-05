import re

from zope import interface
from zope import schema
from zope import component
from megrok.form.fields import Email

from horae.auth import _


class ISelectableRoleProvider(interface.Interface):
    """ Provider for selectable roles
    """

    def roles():
        """ Returns a list of role names
        """


def unique(id):
    providers = component.getAllUtilitiesRegisteredFor(IGroupProvider)
    for provider in providers:
        group = provider.get_group(id)
        if group is not None:
            return False
    providers = component.getAllUtilitiesRegisteredFor(IUserProvider)
    for provider in providers:
        user = provider.get_user(id)
        if user is not None:
            return False
    return True


class IGroup(interface.Interface):
    """ A group
    """

    id = schema.TextLine(
        title=_(u'ID'),
        required=True
    )
    """ The unique id of the group
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )
    """ The name of the group
    """

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )
    """ An optional description for the group
    """

    roles = schema.Set(
        title=_(u'Roles'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.roles'
        )
    )
    """ A set of roles this group is assigned to
    """

    @interface.invariant
    def groupidValid(group):
        if not unique(group.id):
            raise interface.Invalid(_(u'The entered ID is already in use'))


class IGroupProvider(interface.Interface):
    """ Provider for available groups
    """

    def groups():
        """ Returns a list of groups providing :py:class:`IGroup`
        """

    def get_group(id):
        """ Returns the :py:class:`IGroup` with the specified id or None
        """


class IUser(interface.Interface):
    """ A user
    """

    username = schema.TextLine(
        title=_(u'Username'),
        required=True
    )
    """ The users unique username
    """

    name = schema.TextLine(
        title=_(u'Full name'),
        required=False
    )
    """ The name of the user
    """

    email = Email(
        title=_(u'Email'),
        required=True
    )
    """ The Email address of the user
    """

    password = schema.Password(
        title=_(u'Password'),
        required=True
    )
    """ The users password
    """

    groups = schema.Set(
        title=_(u'Groups'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.groups'
        )
    )
    """ A set of :py:class:`IGroup` this user belongs to
    """

    roles = schema.Set(
        title=_(u'Roles'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.roles'
        )
    )
    """ A set of roles this user is assigned to
    """

    @interface.invariant
    def usernameValid(user):
        if re.match(r'[^a-zA-Z0-9\.\-\_]', user.username) is not None:
            raise interface.Invalid(_(u'The entered username is invalid. Only characters, numbers, points, dashes and underlines are allowed'))

    def checkPassword(password):
        """ Checks the provided password
        """


class IUserProvider(interface.Interface):
    """ Provider for available users
    """

    def users():
        """ Returns a list of users providing :py:class:`IUser`
        """

    def get_user(username):
        """ Returns the :py:class:`IUser` with the specified username or None
        """


class ILoginForm(interface.Interface):
    """ A login form
    """

    login = schema.BytesLine(
        title=_(u'Username'),
        required=True
    )
    """ The username to be used to log in
    """

    password = schema.Password(
        title=_(u'Password'),
        required=True
    )
    """ The password to be used to log in
    """


class IShareable(interface.Interface):
    """ Marker interface for shareable objects
    """


class ISharingModifiedEvent(component.interfaces.IObjectEvent):
    """ An objects sharing has been modified
    """


class IUserURL(interface.Interface):
    """ URL of a user
    """

    def __call__():
        """ Returns the URL for the user
        """


class IStartPage(interface.Interface):
    """ URL to be redirected to after login
    """

    def __call__():
        """ Returns the URL
        """
