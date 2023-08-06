"""Clients"""

import datetime
import grok

from zope.interface import Interface
from zope.component import getMultiAdapter, getUtility
from zope.intid.interfaces import IIntIds

from zc.relation.interfaces import ICatalog

from z3c.relationfield.interfaces import IHasIncomingRelations

import merlot.interfaces as ifaces
from merlot.lib import master_template, default_form_template
from merlot import MerlotMessageFactory as _


class ClientContainer(grok.Container):
    grok.implements(ifaces.IClientContainer)

    def __init__(self, title=None):
        super(ClientContainer, self).__init__()
        self.next_id = 1
        if title:
            self.title = title


class ClientContainerIndex(grok.View):
    """The clients container view"""
    grok.context(ifaces.IClientContainer)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template


class ClientContainerIndexViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IClientContainer)
    grok.template('clientcontainer_index')
    grok.view(ClientContainerIndex)
    grok.order(10)


class Client(grok.Model):
    """The simple client type"""
    grok.implements(ifaces.IClient, ifaces.IMetadata, ifaces.ISearchable,
                    IHasIncomingRelations)
    content_type = 'Client'

    @property
    def projects(self):
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        rels = catalog.findRelations({'to_id': intids.getId(self)})
        return [r.from_object for r in rels]


# The add client form, view and viewlet
class AddClientForm(grok.AddForm):
    grok.context(ifaces.IClientContainer)
    grok.name('add-client-form')
    form_fields = grok.AutoFields(ifaces.IClient)
    label = _(u'Create a new client')
    template = default_form_template

    @grok.action(_(u'Add client'))
    def add(self, **data):
        client = Client()
        client.creator = self.request.principal.title
        client.creation_date = datetime.datetime.now()
        client.modification_date = datetime.datetime.now()
        self.applyData(client, **data)

        id = str(self.context.next_id)
        client.id = id
        self.context.next_id = self.context.next_id + 1
        self.context[id] = client

        self.flash(_(u'Client added.'), type=u'message')
        return self.redirect(self.url(self.context))

    def setUpWidgets(self, ignore_request=False):
        super(AddClientForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50


class AddClient(grok.View):
    grok.context(ifaces.IClientContainer)
    grok.name('add-client')
    grok.require('merlot.Manage')
    template = master_template


class AddClientViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(AddClient)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='add-client-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


# The edit client form, view and viewlet
class EditClientForm(grok.EditForm):
    grok.context(ifaces.IClient)
    grok.name('edit-form')
    form_fields = grok.AutoFields(ifaces.IClient)
    label = _(u'Edit the client')
    template = default_form_template

    def setUpWidgets(self, ignore_request=False):
        super(EditClientForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50

    @grok.action(_('Save'))
    def edit(self, **data):
        self.context.modification_date = datetime.datetime.now()
        self.applyData(self.context, **data)
        self.flash(_(u'Changes saved.'), type=u'message')
        return self.redirect(self.url(self.context))


class EditClient(grok.View):
    grok.context(ifaces.IClient)
    grok.name('edit')
    grok.require('merlot.Manage')
    template = master_template


class EditClientViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IClient)
    grok.view(EditClient)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='edit-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class ClientIndex(grok.View):
    """The client view"""
    grok.context(ifaces.IClient)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template

    def update(self):
        return


class ClientIndexViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IClient)
    grok.template('client_index')
    grok.view(ClientIndex)
    grok.order(10)

    def update(self):
        self.projects = self.context.projects


class DeleteClient(grok.View):
    """Delete the client and return to the dashboard"""

    grok.context(ifaces.IClient)
    grok.name('delete')
    grok.require('merlot.Manage')

    def render(self):
        clients = self.context.__parent__
        if not self.context.projects:
            del clients[self.context.id]
            self.flash(_(u'Client deleted.'), type=u'message')
            return self.redirect(self.url(clients))
        else:
            self.flash(_(u'This client cannot be deleted because it has '
                          'projects associated'), type=u'message')
            return self.redirect(self.url(self.context))
