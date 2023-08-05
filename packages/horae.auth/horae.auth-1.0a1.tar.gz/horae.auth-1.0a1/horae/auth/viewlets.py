import grok

from zope.interface import Interface
from zope.authentication.interfaces import IUnauthenticatedPrincipal

from horae.layout import layout
from horae.layout.viewlets import TopManager

from horae.auth.utils import getUser
from horae.auth.interfaces import IUserURL

grok.templatedir('viewlet_templates')
grok.context(Interface)


class LoginLogout(layout.Viewlet):
    """ A viewlet displaying a link to the login form if the current user
        is not logged in or a link to the users page and to log out if the
        user is logged in
    """
    grok.viewletmanager(TopManager)
    grok.order(30)

    def update(self):
        self.dorender = not self.view.__name__ == 'login'
        self.loggedin = not IUnauthenticatedPrincipal.providedBy(self.request.principal)
        if self.loggedin:
            user = getUser(self.request.principal.id)
            self.user = user is not None and user.name or self.request.principal.id
            self.user_url = IUserURL(user, lambda: None)()
        else:
            self.login = '@@login?camefrom=%s' % self.view.url(self.context)
