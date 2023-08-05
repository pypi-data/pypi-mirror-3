import grok

from horae.auth import _


class Manager(grok.Role):
    grok.name('horae.Manager')
    grok.title(_(u'Manager'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.Delete',
        'horae.ViewHistory',
        'horae.AddClient',
        'horae.AddProject',
        'horae.AddMilestone',
        'horae.AddTicket',
        'horae.ChangeTicket',
        'horae.ViewHiddenProperties',
        'horae.Manage',
        'horae.ManageGroups',
        'horae.ManageUsers',
        'horae.Sharing')


class Administrator(grok.Role):
    grok.name('horae.Administrator')
    grok.title(_(u'Administrator'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.Delete',
        'horae.ViewHistory',
        'horae.AddClient',
        'horae.AddProject',
        'horae.AddMilestone',
        'horae.AddTicket',
        'horae.ChangeTicket',
        'horae.ViewHiddenProperties',
        'horae.ManageUsers',
        'horae.Sharing')


class Owner(grok.Role):
    grok.name('horae.Owner')
    grok.title(_(u'Owner'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.Manage',)

# local roles


class Member(grok.Role):
    grok.name('horae.Member')
    grok.title(_(u'Member'))
    grok.permissions()


class Reader(grok.Role):
    grok.name('horae.Reader')
    grok.title(_(u'Reader'))
    grok.permissions(
        'horae.View',
        'horae.ViewHistory')


class Editor(grok.Role):
    grok.name('horae.Editor')
    grok.title(_(u'Editor'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.ViewHistory',
        'horae.ChangeTicket')


class Contributor(grok.Role):
    grok.name('horae.Contributor')
    grok.title(_(u'Contributor'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.Delete',
        'horae.AddClient',
        'horae.AddProject',
        'horae.AddMilestone',
        'horae.AddTicket',
        'horae.ViewHistory',
        'horae.ChangeTicket')


class TicketEditor(grok.Role):
    grok.name('horae.TicketEditor')
    grok.title(_(u'Ticket editor'))
    grok.permissions(
        'horae.View',
        'horae.AddTicket',
        'horae.ViewHistory',
        'horae.ChangeTicket')


class Reponsible(grok.Role):
    grok.name('horae.Responsible')
    grok.title(_(u'Responsible'))
    grok.permissions(
        'horae.View',
        'horae.Edit',
        'horae.ViewHistory',
        'horae.ChangeTicket')
