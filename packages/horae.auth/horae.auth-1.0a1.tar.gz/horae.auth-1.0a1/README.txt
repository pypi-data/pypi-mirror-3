Introduction
============

The ``horae.auth`` package provides a pluggable users and groups architecture for the Horae
resource planning system and includes the following functionality:

* Provides an authenticator and session credentials plugin using
  `zope.pluggableauth <http://pypi.python.org/pypi/zope.pluggableauth>`_
* Defines default roles and permissions for Horae
* Defines generic interfaces for users and groups and hooks for additional packages to provide them
* Provides basic login and logout views based on `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* Sharing

Authenticator and session credentials plugin
============================================

Both plugins are defined in ``horae.auth.auth`` and setup by the ``horae.auth.auth.setup_authentication``
function. To use the plugins they have to be registered with the grok application which the following
example illustrates::

    import grok
    from zope.app.authentication.authentication import (
        PluggableAuthentication)
    from zope.app.security.interfaces import IAuthentication
    
    from horae.auth import auth
    
    class SampleApplication(grok.Application):
        grok.local_utility(PluggableAuthentication,
                           provides=IAuthentication,
                           setup=auth.setup_authentication)

Roles and permissions
=====================

The following default permissions are defined by ``horae.auth``:

**View**
  Permission required to view an object
**Edit**
  Permission required to edit an object
**Delete**
  Permission required to delete an object
**ViewHistory**
  Permission required to view the history of an object
**AddClient**
  Permission required to add a client
**AddProject**
  Permission required to add a project
**AddMilestone**
  Permission required to add a milestone
**AddTicket**
  Permission required to add a ticket
**ChangeTicket**
  Permission required to change a ticket
**ViewHiddenProperties**
  Permission required to view hidden properties
**Manage**
  Management permission
**ManageGroups**
  Permission required to manage groups
**ManageUsers**
  Permission required to manage users
**Sharing**
  Permission required to share objects

Based on those permissions the following roles are defined:

**Manager**
  View, Edit, Delete, ViewHistory, AddClient, AddProject, AddMilestone, AddTicket, ChangeTicket, ViewHiddenProperties, Manage, ManageGroups, ManageUsers, Sharing
**Administrator**
  View, Edit, Delete, ViewHistory, AddClient, AddProject, AddMilestone, AddTicket, ChangeTicket, ViewHiddenProperties, ManageUsers, Sharing
**Owner**
  View, Edit, Manage
**Member**
  Assigned to every user
**Reader**
  View, ViewHistory
**Editor**
  View, Edit, ViewHistory, ChangeTicket
**Contributor**
  View, Edit, Delete, AddClient, AddProject, AddMilestone, AddTicket, ViewHistory, ChangeTicket
**TicketEditor**
  View, AddTicket, ViewHistory, ChangeTicket
**Responsible**
  View, Edit, ViewHistory, ChangeTicket

Generic interfaces and hooks
============================

The main interfaces defined by ``horae.auth`` are:

* ``horae.auth.interfaces.IUser``
* ``horae.auth.interfaces.IGroup``
* ``horae.auth.interfaces.IUserProvider``
* ``horae.auth.interfaces.IGroupProvider``

``horae.auth`` does not provide any implementation of those interfaces which is done by
packages like `horae.usersandgroups <http://pypi.python.org/pypi/horae.usersandgroups>`_.
This architecture makes it possible to quite easily plug in new user and group sources
such as LDAP [#]_.

As mentioned above a sample implementation may be found in the package `horae.usersandgroups
<http://pypi.python.org/pypi/horae.usersandgroups>`_ which provides persistent users
and groups and basic CRUD [#]_ functionality.

Sharing
=======

Marking objects as shareable (implementing ``horae.auth.interfaces.IShareable``)
makes it possible to grant roles for users and groups on the specific object. The roles
are inherited from parent objects by default making it possible to grant a role for an
object and all its childs. Role inheritance may be disabled individually for shareable
objects. The roles available to be granted are defined by named utilities implementing
``horae.auth.interfaces.ISelectableRoleProvider``. The default implementation is located
at ``horae.auth.auth`` and looks like this::

    from horae.auth import interfaces
    
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

and thus makes the roles ``Reader``, ``Editor``, ``Contributor`` and ``TicketEditor`` available
to be granted for shareable objects. To make other roles available additional providers may be
registered::

    class SampleSelectableRoleProvider(grok.GlobalUtility):
        """ Provider for selectable roles
        """
        grok.implements(interfaces.ISelectableRoleProvider)
        grok.provides(interfaces.ISelectableRoleProvider)
        grok.name('horae.sampleadditionalroles.selectableroles')
    
        def roles(self):
            """ Returns a list of role names
            """
            return ['horae.SampleRole1', 'horae.SampleRole2']

Enabling the sharing functionality on an object is simply done by letting it implement the marker
interface ``horae.auth.interfaces.IShareable``. This may be done by having the class directly
implement the interface::

    class MyShareableContent(grok.Model):
        grok.implements(interfaces.IShareable)

or by doing so from outside the class definition which is especially usable if the desired class
is part of a module not related to ``horae.auth``::

    from zope.interface import classImplements
    
    from some.other.unrelated.module import OtherContent
    
    classImplements(OtherContent, interfaces.IShareable)

Dependencies
============

Horae
-----

* `horae.cache <http://pypi.python.org/pypi/horae.cache>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `zope.pluggableauth <http://pypi.python.org/pypi/zope.pluggableauth>`_

.. [#] `Lightweight Directory Access Protocol <http://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol>`_
.. [#] **C**\ reate **R**\ ead **U**\ pdate **D**\ elete.
