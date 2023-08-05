import grok

# Ticketing


class View(grok.Permission):
    grok.name('horae.View')


class Edit(grok.Permission):
    grok.name('horae.Edit')


class Delete(grok.Permission):
    grok.name('horae.Delete')


class ViewHistory(grok.Permission):
    grok.name('horae.ViewHistory')


class AddClient(grok.Permission):
    grok.name('horae.AddClient')


class AddProject(grok.Permission):
    grok.name('horae.AddProject')


class AddMilestone(grok.Permission):
    grok.name('horae.AddMilestone')


class AddTicket(grok.Permission):
    grok.name('horae.AddTicket')


class ChangeTicket(grok.Permission):
    grok.name('horae.ChangeTicket')


class ViewHiddenProperties(grok.Permission):
    grok.name('horae.ViewHiddenProperties')

# Configuration


class Manage(grok.Permission):
    grok.name('horae.Manage')

# User & Groups


class ManageGroups(grok.Permission):
    grok.name('horae.ManageGroups')


class ManageUsers(grok.Permission):
    grok.name('horae.ManageUsers')


class Sharing(grok.Permission):
    grok.name('horae.Sharing')
