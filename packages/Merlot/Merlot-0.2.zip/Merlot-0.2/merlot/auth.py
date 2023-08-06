"""Authentication and authorization.

A simple session based authentication and authorization mechanism is
used.

You will find here definitions of the models and views related to
authentication and authorization.
"""

import grok
from zope import component
from zope.interface import Interface, Invalid

from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import ILogout
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope.component import getMultiAdapter

from merlot.lib import master_template, default_form_template
import merlot.interfaces as ifaces
from merlot import MerlotMessageFactory as _


def setup_authentication(pau):
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['users']


class MySessionCredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.username'
    passwordfield = 'form.password'


class LoginForm(grok.Form):
    """The login form"""
    grok.name('login-form')
    grok.context(Interface)
    label = _(u'Login')
    template = default_form_template

    form_fields = grok.Fields(ifaces.ILoginForm)

    def setUpWidgets(self, ignore_request=False):
        super(LoginForm, self).setUpWidgets(ignore_request)
        self.widgets['camefrom'].type = 'hidden'

    @grok.action(_('Login'))
    def handle_login(self, **data):
        authenticated = not IUnauthenticatedPrincipal.providedBy(
            self.request.principal,
        )
        if authenticated:
            self.redirect(self.request.form.get('camefrom',
                                                self.url(grok.getSite())))
            self.flash(_(u'You are logged in.'), type=u'message')
        else:
            self.status = _(u'Login failed.')
            self.errors += (Invalid(u'Invalid username and/or password'),)
            self.form_reset = False


class Login(grok.View):
    """The login view"""
    grok.context(Interface)
    grok.require('zope.Public')
    template = master_template


class LoginViewlet(grok.Viewlet):
    """The login viewlet, which renders the login form and is
    registered for the Login view.
    """
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(Login)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='login-form',)
        self.form.update_form()

    def render(self):
        return self.form.render()


class Logout(grok.View):
    """The logout view"""
    grok.context(Interface)
    grok.require('merlot.Manage')

    def render(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)

        self.flash(_(u'You are now logged out'), type=u'message')
        return self.redirect(self.application_url())


class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None


class UserAuthenticatorPlugin(grok.LocalUtility):
    """A local utility to manage users"""
    grok.implements(IAuthenticatorPlugin)
    grok.name('users')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        account = self.getAccount(credentials['login'])

        if account is None:
            return None
        if not account.checkPassword(credentials['password']):
            return None
        return PrincipalInfo(id=account.id,
                             title=account.real_name,
                             description=account.real_name)

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return None
        return PrincipalInfo(id=account.id,
                             title=account.real_name,
                             description=account.real_name)

    def getAccount(self, username):
        user_folder = grok.getSite()['users'] if 'users' \
                      in grok.getSite() else ''
        return username in user_folder and user_folder[username] or None

    def addUser(self, username, password, real_name):
        user_folder = grok.getSite()['users']
        if username not in user_folder:
            user = Account(username, password, real_name)
            user_folder[username] = user
            role_manager = IPrincipalRoleManager(grok.getSite())
            role_manager.assignRoleToPrincipal('merlot.Manager', username)

    def removeUser(self, username):
        user_folder = grok.getSite()['users']
        if username in user_folder:
            role_manager = IPrincipalRoleManager(grok.getSite())
            role_manager.removeRoleFromPrincipal('merlot.Manager', username)
            del user_folder[username]


class UserFolder(grok.Container):
    grok.implements(ifaces.IUserFolder)

    def __init__(self, title=None):
        super(UserFolder, self).__init__()
        self.title = title


class UserFolderIndex(grok.View):
    """The users container view"""
    grok.context(ifaces.IUserFolder)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template


class UserFolderIndexViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IUserFolder)
    grok.template('userfolder_index')
    grok.view(UserFolderIndex)
    grok.order(10)


class Account(grok.Model):
    grok.implements(ifaces.IAccount)
    content_type = 'Account'

    def __init__(self, username, password, real_name):
        self.id = username
        self.real_name = real_name
        self.setPassword(password)

    def setPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        self.password = passwordmanager.encodePassword(password)

    def checkPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager, 'SHA1')
        return passwordmanager.checkPassword(self.password, password)


class AddUserForm(grok.AddForm):
    """The add user form"""
    grok.context(ifaces.IUserFolder)
    grok.name('add-user-form')
    label = _(u'Add user')
    template = default_form_template

    form_fields = grok.Fields(ifaces.IAddUserForm)

    @grok.action(_(u'Add user'))
    def handle_add(self, **data):
        users = component.getUtility(IAuthenticatorPlugin, 'users')
        users.addUser(data['id'], data['password'], data['real_name'])
        self.flash(_(u'User added.'), type=u'message')
        self.redirect(self.url(self.context))


class AddUser(grok.View):
    """The add user view"""
    grok.context(ifaces.IUserFolder)
    grok.name('add-user')
    grok.require('merlot.Manage')
    template = master_template


class AddUserViewlet(grok.Viewlet):
    """The add user viewlet, which renders the add user form and is
    registered for the AddUser view.
    """
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IUserFolder)
    grok.view(AddUser)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='add-user-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class EditUserForm(grok.Form):
    """The edit user form"""
    grok.context(ifaces.IAccount)
    grok.name('edit-user-form')
    label = _(u'Edit user')
    template = default_form_template

    form_fields = grok.Fields(ifaces.IEditUserForm)

    @grok.action(_(u'Save'))
    def edit(self, **data):
        password = self.request.form.get('form.password')
        if password:
            self.context.setPassword(password)
        self.context.real_name = self.request.form.get('form.real_name')
        self.flash(_(u'Changes saved.'), type=u'message')
        return self.redirect(self.url(self.context.__parent__))

    def setUpWidgets(self, ignore_request=False):
        super(EditUserForm, self).setUpWidgets(ignore_request)
        self.widgets['id'].setRenderedValue(self.context.id)
        self.widgets['real_name'].setRenderedValue(self.context.real_name)
        self.widgets['id'].extra = 'readonly="true"'
        self.widgets['password'].setRenderedValue('')


class EditUser(grok.View):
    """The edit user view"""
    grok.context(ifaces.IAccount)
    grok.name('edit')
    grok.require('merlot.Manage')
    template = master_template


class EditUserViewlet(grok.Viewlet):
    """The edit user viewlet, which renders the edit user form and is
    registered for the EditUser view.
    """
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IAccount)
    grok.view(EditUser)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='edit-user-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class DeleteUser(grok.View):
    """Delete a user and return to the manage users screen"""

    grok.context(ifaces.IAccount)
    grok.name('delete')
    grok.require('merlot.Manage')

    def render(self):
        userfolder = self.context.__parent__
        users = component.getUtility(IAuthenticatorPlugin, 'users')
        users.removeUser(self.context.id)

        self.flash(_(u'User deleted.'), type=u'message')
        return self.redirect(self.url(userfolder))


class ManagerPermission(grok.Permission):
    """The manage permission"""
    grok.name('merlot.Manage')


class ManagerRole(grok.Role):
    """The manager role"""
    grok.name('merlot.Manager')
    grok.permissions('merlot.Manage')
