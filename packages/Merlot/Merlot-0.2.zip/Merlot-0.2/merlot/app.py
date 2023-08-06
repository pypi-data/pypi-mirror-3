# -*- coding: utf-8 -*-
"""A Grok application to manage projects.

In this module it's defined the Grok application class and the elements
that will be repeated all over the application such as viewlet
managers, common viewlets like the path bar, the personal bar, among
others.
"""

from datetime import datetime
import logging

import grok

from zope.interface import Interface
from zope import schema
from zope.component import getUtility, getMultiAdapter
from zope.security.interfaces import IUnauthorized
from zope.i18n import translate

from zope.intid import IntIds
from zope.intid.interfaces import IIntIds
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin

from zc.relation.interfaces import ICatalog as IRelationCatalog
from z3c.relationfield import RelationCatalog
from zope.catalog.interfaces import ICatalog

from z3c.objpath.interfaces import IObjectPath
from z3c.objpath import path, resolve

from z3c.flashmessage.interfaces import IMessageReceiver

from merlot.auth import UserAuthenticatorPlugin, setup_authentication
from merlot.project import ProjectContainer
from merlot.client import ClientContainer
from merlot.auth import UserFolder
import merlot.interfaces as ifaces
from merlot import MerlotMessageFactory as _


class Merlot(grok.Application, grok.Container):
    """The Grok application class"""
    grok.implements(ifaces.IMerlot)

    def __init__(self):
        super(Merlot, self).__init__()
        self.title = _(u'Merlot — Project Management Software')

        projs_container = ProjectContainer(title=u'Projects')
        self['projects'] = projs_container
        orgs_container = ClientContainer(title=u'Clients')
        self['clients'] = orgs_container
        user_folder = UserFolder(title=u'Users')
        self['users'] = user_folder

    # Register local utilities
    grok.local_utility(UserAuthenticatorPlugin,
                       provides=IAuthenticatorPlugin,
                       name='users')
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_authentication)
    grok.local_utility(IntIds, provides=IIntIds, name='intids')
    grok.local_utility(RelationCatalog, provides=IRelationCatalog)


class ObjectPath(grok.GlobalUtility):
    """A global utility to resolve to an object given a path; and to
    return the path of a given object.
    """
    grok.provides(IObjectPath)

    def path(self, obj):
        """Return the path of the given object"""
        return path(grok.getSite(), obj)

    def resolve(self, path):
        """Return the object corresponding the given path"""
        return resolve(grok.getSite(), path)


# Viewlet mangers
class Head(grok.ViewletManager):
    """The head viewlet manager.

    Here goes what goes in the head tag of the HTML document.
    """
    grok.implements(ifaces.IHead)
    grok.context(Interface)
    grok.name('head')


class Header(grok.ViewletManager):
    """The header viewlet manager.

    The top part of the body tag element of the HTML document, where you
    usually put the logo.
    """
    grok.implements(ifaces.IHeader)
    grok.context(Interface)
    grok.name('header')


class Main(grok.ViewletManager):
    """The main content area viewlet manager"""
    grok.implements(ifaces.IMain)
    grok.context(Interface)
    grok.name('main')


class Footer(grok.ViewletManager):
    """A viewlet manager for the footer"""
    grok.implements(ifaces.IFooter)
    grok.context(Interface)
    grok.name('footer')


# Viewlets that will be used application wide
class HeadViewlet(grok.Viewlet):
    """A viewlet to render what goes in the head tag of the HTML
    document.
    """
    grok.viewletmanager(ifaces.IHead)
    grok.context(Interface)
    grok.template('head')


class Logo(grok.Viewlet):
    """A viewlet for the logo"""
    grok.viewletmanager(ifaces.IHeader)
    grok.context(Interface)


class PersonalBar(grok.Viewlet):
    """A viewlet for the personal bar"""
    grok.viewletmanager(ifaces.IHeader)
    grok.context(Interface)
    grok.require('merlot.Manage')

    def update(self):
        self.td = datetime.now().strftime('%Y-%m-%d')


class NavigationBar(grok.Viewlet):
    """A viewlet for the navigation bar"""
    grok.viewletmanager(ifaces.IHeader)
    grok.context(Interface)
    grok.require('merlot.Manage')
    grok.order(2)

    def update(self):
        sections = []
        sections = [
            {'title': '',
             'url': self.view.application_url(),
             'css':'home',
             'id':'index'},
            {'title': _('Projects'),
             'url': self.view.application_url() + '/projects',
             'css':'projects',
             'id':'projects'},
            {'title': _('Reports'),
             'url':self.view.application_url() + '/reports',
             'css':'reports',
             'id':'reports'},
            {'title': _('Clients'),
             'url':self.view.application_url() + '/clients',
             'css':'clients',
             'id':'clients'},
            {'title': _('Users'),
             'url':self.view.application_url() + '/users',
             'css':'users',
             'id':'manage-users'}]
        self.sections = sections

        ids_list = ['projects', 'reports', 'clients', 'manage-users', 'index']
        url = self.view.url()[len(self.view.application_url()):]
        url_list = url.split('/')
        self.path = []
        for obj_id in url_list:
            if obj_id in ids_list:
                self.path = [obj_id]
                break


class PathBar(grok.Viewlet):
    """A viewlet for the path bar"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.require('merlot.Manage')
    grok.order(0)

    def update(self):
        path = []
        current = self.context
        while not ifaces.IMerlot.providedBy(current):
            title = ''
            if ifaces.IProjectContainer.providedBy(current):
                title = _(u'Projects')
            elif ifaces.IUserFolder.providedBy(current):
                title = _(u'Users')
            elif ifaces.IClientContainer.providedBy(current):
                title = _(u'Clients')
            elif ifaces.IAccount.providedBy(current):
                title = current.real_name
            elif hasattr(current, 'title'):
                title = current.title
            else:
                title = current.id

            path.insert(0,
                {'title': title,
                 'url': self.view.url(current),
                })
            current = current.__parent__
        path.insert(0,
            {'title': _('Home'),
             'url': self.view.application_url(),
            })
        self.path = path


class FlashMessages(grok.Viewlet):
    """A viewlet for the flash messages"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    #grok.require('merlot.Manage')
    grok.order(1)

    def update(self):
        receiver = getUtility(IMessageReceiver)

        self.messages = []
        self.errors = []

        # XXX: For some reason, messages get consumed twice when
        # submitting a form, causing that some messages never make it to
        # the UI. This is a workaround to avoid that behaviour, if there
        # are no keys starting with 'form' in the request, we don't
        # consume any messages.
        if not [i for i in self.request.keys() if i.startswith('form')]:
            self.messages = [m.message for m in receiver.receive(u'message')]
            self.errors = [m.message for m in receiver.receive(u'error')]


class FooterViewlet(grok.Viewlet):
    """A viewlet for the footer content"""
    grok.viewletmanager(ifaces.IFooter)
    grok.context(Interface)
    grok.template('footer')


# The application home page
class Index(grok.View):
    """This is the application home page"""
    grok.require('merlot.Manage')
    grok.template('master')

    def update(self):
        # Build a list with all the starred tasks for the authenticated
        # user.
        self.starred_tasks = []
        users = getUtility(IAuthenticatorPlugin, 'users')
        intids = getUtility(IIntIds, name='intids')
        user = users.getAccount(self.request.principal.id)

        if user:
            starred_tasks = ifaces.IStarredTasks(user)

            for task_intid in starred_tasks.getStarredTasks():
                task = intids.getObject(task_intid)
                self.starred_tasks.append(task)

        # Build a list with the latest tasks where the user logged some
        # hours.
        query = {'content_type': ('Log', 'Log')}
        user = self.request.principal.id
        if user:
            query['user'] = (user, user)
        catalog = getUtility(ICatalog)
        logs_brain = catalog.searchResults(**query)
        logs_list = [log for log in logs_brain]
        logs_list.sort(cmp=lambda x, y: cmp(x.modification_date,
                                            y.modification_date))
        logs_list.reverse()

        self.latest_tasks = []
        for log in logs_list:
            task = log.__parent__
            if not task in self.latest_tasks and \
               task not in self.starred_tasks:
                self.latest_tasks.append(task)

        self.tasks = self.starred_tasks + self.latest_tasks

    def projects(self, task):
        intids = getUtility(IIntIds, name='intids')
        project = intids.getObject(task.project())
        self.project_id = project.id
        self.project_title = project.title
        return project


class Unauthorized(grok.View):
    grok.context(IUnauthorized)
    grok.name("index.html")
    grok.require("zope.Public")

    def render(self):
        principal = self.request.principal
        auth = getUtility(IAuthentication)
        auth.unauthorized(principal.id, self.request)
        if self.request.response.getStatus() not in (302, 303):
            return _('Not authorized!')


# The delete confirmation view, form and main viewlet
class DeleteConfirmation(grok.View):
    grok.context(Interface)
    grok.name('confirm-delete')
    grok.template('master')
    grok.require('merlot.Manage')


class DeleteConfirmationForm(grok.Form):
    grok.context(Interface)
    grok.name('confirm-delete-form')

    class ContextField(Interface):
        context = schema.TextLine(title=u'', required=False)
        id = schema.TextLine(title=u'', required=False)

    form_fields = grok.AutoFields(ContextField)

    def setUpWidgets(self, ignore_request=False):
        super(DeleteConfirmationForm, self).setUpWidgets(ignore_request)

        context = self.request.get('context', None)
        self.widgets['context'].setRenderedValue(context)
        self.widgets['context'].type = 'hidden'

        id = self.request.get('id', None)
        self.widgets['id'].setRenderedValue(id)
        self.widgets['id'].type = 'hidden'

        item = ''
        if hasattr(self.context, 'content_type') and \
           self.context.content_type == 'Log':
            item = 'log'
        elif id:
            item = '"%s"' % id
        elif hasattr(self.context, 'title'):
            item = '"%s"' % self.context.title
        else:
            item = '"%s"' % self.context.id
        qst = _('Are you sure you want to delete the ${name} item?',
                mapping={u'name': item})
        self.label = qst

    @grok.action(_(u'Delete'))
    def delete(self, **data):
        """Redirect to the delete view"""
        context = data.get('context', None)
        id = data.get('id', None)
        redirect_to = ''
        if context == 'log':
            redirect_to = self.url(self.context) + \
                '/@@delete-log/?id=%s' % id
        else:
            redirect_to = self.url(self.context) + '/delete'
        return self.redirect(redirect_to)

    @grok.action(_('Cancel'))
    def cancel(self, **data):
        """Redirect to where you came from"""
        if self.context.content_type in ['Log', 'Account']:
            return self.redirect(self.url(self.context.__parent__))
        else:
            return self.redirect(self.url(self.context))


class DeleteConfirmationViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(DeleteConfirmation)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='confirm-delete-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class IndexViewlet(grok.Viewlet):
    """A viewlet for the dashboard.

    It will be rendered in the home page.
    """
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IMerlot)
    grok.template('dashboard')
    grok.view(Index)
    grok.order(10)


class ControlPanel(grok.View):
    """The application control panel"""
    grok.name('control-panel')
    grok.require('merlot.Manage')
    grok.template('master')


class ControlPanelViewlet(grok.Viewlet):
    """The main viewlet of the control panel"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IMerlot)
    grok.template('control_panel')
    grok.view(ControlPanel)
    grok.order(10)


# Based in https://svn.plone.org/svn/collective/Products.PloneFormGen/trunk/Products/PloneFormGen/browser/jsvariables.py
# thanks Steve McMahon http://www.stevemcmahon.com/
class I18nJavascript(grok.View):
    grok.context(Interface)
    grok.name('i18n-js')
    grok.require('merlot.Manage')

    def render(self):
        messages = {
            'DELETE_I18N': _('delete'),
            'SUCCESS_I18N': _('The log was successfully saved'),
            'MORE_I18N': _('Add another log to this task'),
            'ENTER_DATE_HERE_I18N': _("Enter a date here"),
            'TYPE_DATE_BELOW_I18N': _("Type a date below"),
            'TODAY_I18N': _('Today'),
            'LAST_7_DAYS_I18N': _('Last 7 days'),
            'MONTH_TO_DATE_I18N': _('Month to date'),
            'PREVIOUS_MONTH_I18N': _('The previous month'),
            'DATE_RANGE_I18N': _('Date Range'),
            'SPECIFIC_DATE_I18N': _('Specific Date'),
            'DUE_IN_I18N': _('Due in'),
            'HOURS_USAGE_I18N': _('Hours Usage'),
            'DAYS_BEHIND_I18N': _('days behind'),
            'DAY_BEHIND_I18N': _('day behind'),
            'DAYS_I18N': _('days'),
            'DAY_I18N': _('day'),
            'NO_DEADLINE_I18N': _('Deadline not set'),
            'HOURS_I18N': _('hours'),
            'COMPLETED_I18N': _('Completed')}
        message_variable = "merlot = {};merlot.i18n = {\n%s}\n"
        response = self.request.response
        response.setHeader('Content-Type', 'text/javascript; charset=UTF-8')
        template = ''
        for key in messages:
            msg = translate(messages[key],
                            context=self.request).replace("'", "\\'")
            template = "%s%s: '%s',\n" % (template, key, msg)

        return message_variable % template[:-2]


#class DataMigration(grok.View):
#    """Migrate Data.fs' that existed previous to moving the source to
#    the current repo.
#    """
#    grok.context(Interface)
#    grok.name('data-migration-pre-hg')
#
#    def render(self):
#        site = grok.getSite()
#
#        # Add priority attribute to tasks
#        query = {'content_type': ('Task', 'Task')}
#        catalog = getUtility(ICatalog)
#        tasks = catalog.searchResults(**query)
#        for task in tasks:
#            task.priority = u'Normal'
#
#        # Migrate user folder
#        if not 'users' in site.keys():
#            user_folder = UserFolder(title=u'Users')
#            logging.info('Getting old users folder...')
#            old_user_folder = getUtility(IAuthenticatorPlugin, \
#                'users').user_folder
#            logging.info('Done, old users found:' + \
#                str([x for x in old_user_folder]))
#            for user_key in old_user_folder:
#                user_folder[user_key] = old_user_folder[user_key]
#            site['users'] = user_folder
#
#            logging.info('Checking attributes...')
#            for account in user_folder:
#                user_folder[account].id = user_folder[account].name
#                del user_folder[account].name
#            del old_user_folder
#            logging.info('Data migrated successfully.')
#        else:
#            logging.info('Old data already migrated?')
#            logging.warning('Nothing done, exiting.')
