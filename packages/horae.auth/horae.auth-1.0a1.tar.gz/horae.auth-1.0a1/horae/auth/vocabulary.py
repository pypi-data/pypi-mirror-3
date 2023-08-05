import grok

from zope.schema import vocabulary
from zope import component
from zope.securitypolicy.interfaces import IRole
from zope.i18n import translate

from horae.core import utils
from horae.cache.vocabulary import cache_global, invalidate_global

from horae.auth import _
from horae.auth.utils import getGroups, getUsers
from horae.auth import interfaces


@cache_global
def roles_vocabulary_factory(context):
    """ A vocabulary of all available roles registered as
        **horae.auth.vocabulary.roles**
    """
    terms = []
    roles = component.getAllUtilitiesRegisteredFor(IRole)
    for role in roles:
        terms.append(vocabulary.SimpleTerm(role.id, role.id, role.title or role.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.roles', roles_vocabulary_factory)


@cache_global
def groups_vocabulary_factory(context):
    """ A vocabulary of all available :py:class:`horae.auth.interfaces.IGroup` registered as
        **horae.auth.vocabulary.groups**
    """
    terms = []
    for group in getGroups():
        terms.append(vocabulary.SimpleTerm(group, group.id, group.name or group.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.groups', groups_vocabulary_factory)


@cache_global
def groupids_vocabulary_factory(context):
    """ A vocabulary of IDs of all available :py:class:`horae.auth.interfaces.IGroup`
        registered as **horae.auth.vocabulary.groupids**
    """
    terms = []
    for group in getGroups():
        terms.append(vocabulary.SimpleTerm(group.id, group.id, group.name or group.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.groupids', groupids_vocabulary_factory)


@grok.subscribe(interfaces.IGroup, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.IGroup, grok.IObjectMovedEvent)
def invalidate_group_vocabulary_cache(obj, event):
    invalidate_global(groups_vocabulary_factory)
    invalidate_global(groupids_vocabulary_factory)


@cache_global
def users_vocabulary_factory(context):
    """ A vocabulary of all available :py:class:`horae.auth.interfaces.IUser` registered as
        **horae.auth.vocabulary.users**
    """
    terms = []
    for user in getUsers():
        terms.append(vocabulary.SimpleTerm(user, user.username, user.name or user.username))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.users', users_vocabulary_factory)


@cache_global
def usernames_vocabulary_factory(context):
    """ A vocabulary of usernames of all available :py:class:`horae.auth.interfaces.IUser`
        registered as **horae.auth.vocabulary.usernames**
    """
    terms = []
    for user in getUsers():
        terms.append(vocabulary.SimpleTerm(user.username, user.username, user.name or user.username))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.usernames', usernames_vocabulary_factory)


def usernamesandme_vocabulary_factory(context):
    """ A vocabulary of usernames of all available :py:class:`horae.auth.interfaces.IUser`
        and an additional term named Me registered as **horae.auth.vocabulary.usernamesandme**
    """
    terms = []
    try:
        terms.append(vocabulary.SimpleTerm(u'me', u'me', translate(_(u'Me'), context=utils.getRequest())))
    except:
        pass
    for user in getUsers():
        terms.append(vocabulary.SimpleTerm(user.username, user.username, user.name or user.username))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.usernamesandme', usernamesandme_vocabulary_factory)


@grok.subscribe(interfaces.IUser, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.IUser, grok.IObjectMovedEvent)
def invalidate_user_vocabulary_cache(obj, event):
    invalidate_global(users_vocabulary_factory)
    invalidate_global(usernames_vocabulary_factory)


@cache_global
def selectableroles_vocabulary_factory(context):
    """ A vocabulary of all selectable roles (roles provided by
        :py:class:`horae.auth.interfaces.ISelectableRoleProvider`
        registered as **horae.auth.vocabulary.selectableroles**
    """
    terms = []
    providers = component.getAllUtilitiesRegisteredFor(interfaces.ISelectableRoleProvider)
    for provider in providers:
        for name in provider.roles():
            role = component.queryUtility(IRole, name=name)
            if role is None:
                continue
            terms.append(vocabulary.SimpleTerm(role.id, role.id, role.title or role.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.auth.vocabulary.selectableroles', selectableroles_vocabulary_factory)
