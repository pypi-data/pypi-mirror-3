"""This module defines all the interfaces used in the application.
"""

import re

import grok

from zope import schema
from zope.interface import Interface, invariant, Invalid, Attribute

from z3c.relationfield import RelationChoice
from z3c.relationfieldui import RelationSourceFactory

from merlot import MerlotMessageFactory as _


class IMerlot(Interface):
    """A grok application to manage projects"""
    title = schema.TextLine(title=_(u'Title'), required=True)


class IHead(Interface):
    """Head viewlet manager marker interface"""


class IHeader(Interface):
    """Header viewlet manager marker interface"""


class IMain(Interface):
    """Main viewlet manager marker interface"""


class IFooter(Interface):
    """Footer viewlet manager marker interface"""


# Sources
class ClientSource(RelationSourceFactory):
    """A source whose items are all the existing clients in the Merlot
    application.
    """

    def getTargets(self):
        """The source targets is a list of the client objects"""
        return [b for b in grok.getSite()['clients'].values()]

    def getTitle(self, value):
        """Get the title of a given source item"""
        return value.to_object.title


# from random import randint
# class ColorGenerator():
#     """Color factory generator convert an (R, G, B) tuple to #RRGGBB"""
#
#     def getValues(self):
#         rgb_tuple = (randint(0, 255), randint(0, 255), randint(0, 255))
#         hexcolor = u'#%02x%02x%02x' % rgb_tuple
#         # that's it! '%02x' means zero-padded, 2-digit hex values
#         return hexcolor


# Auth interfaces
class IUserFolder(Interface):
    """A container for objects that will store the system users
    information.
    """
    title = schema.TextLine(title=_(u'Title'), required=True)


class IAccount(Interface):
    """An account object will maintain the data of the system users"""
    id = schema.BytesLine(title=_(u'Username'), required=True)
    real_name = schema.TextLine(title=_(u'Real name'), required=True)
    password = schema.Password(title=_(u'Password'), required=True)


class ILoginForm(Interface):
    """Login form fields"""
    username = schema.BytesLine(title=_(u'Username'), required=False)
    camefrom = schema.BytesLine(title=u'', required=False)
    password = schema.Password(title=_(u'Password'), required=False)


class IAddUserForm(IAccount):
    """Add user form fields and invariants"""
    confirm_password = schema.Password(title=_(u'Confirm password'),
        required=True)

    @invariant
    def matchingPasswords(form):
        """Check that the password and the password confirmation fields
        match.
        """
        # XXX: we need to find out why form.password turns to be
        # something of type 'object' when we leave the field empty
        # in the edit form.
        if type(form.password) != object and \
           form.confirm_password != form.password:
            raise Invalid(_('Passwords does not match'))

    @invariant
    def validUsername(form):
        """Check that the user name is valid"""
        if not re.compile('^[a-z0-9]+$').match(form.id):
            raise Invalid(_('Invalid user name, only characters in [a-z0-9] '
                            'are allowed'))


# I would like to use the same interface for both the add and edit user
# forms, but those two forms have a notable difference: while the
# password and confirm password fields are required in the add form,
# they are not required in the edit form (leaving the fields empty in
# the edit form will keep the user password unchanged).
#
# I tried to implement that difference by doing:
# form_fields['password'].field.required = False in the setUpWidgets
# method, but grok.Fields does not seem to generate copies of the
# fields; instead, both forms end up pointing to the same actual fields.
# So when I go to an edit form the fields are not requrired, when I go
# back to the add form, the field is not required either.
class IEditUserForm(IAddUserForm):
    """Edit user form fields"""
    password = schema.Password(title=_(u'Password'), required=False)
    confirm_password = schema.Password(title=_(u'Confirm password'),
        required=False)


class IMetadata(Interface):
    """An interface to define metadata that we want to store for certain
    objects.
    """
    id = schema.BytesLine(title=_(u'ID'))
    """The ID is a string that identifies the object inside the
    container the object is in.
    """

    creator = schema.TextLine(title=_(u'Creator'))
    """A reference to the user that created the object"""

    creation_date = schema.Datetime(title=_(u'Creation date'))
    """The object creation date"""

    modification_date = schema.Datetime(title=_(u'Modification date'))
    """The last time the object was modified"""


# Simple project interfaces
class IProjectContainer(Interface):
    """A container that contains project objects"""
    title = schema.TextLine(title=_(u'Title'), required=True)


class IProject(Interface):
    """A simple project"""
    title = schema.TextLine(title=_(u'Title'), required=True)
    description = schema.Text(title=_(u'Description'), required=False)
    client = RelationChoice(
        title=_(u'Client'),
        source=ClientSource(),
        required=True
    )
    status = schema.Choice(
        title=_(u'Status'),
        required=True,
        description=_(u'The status the project is in'),
        vocabulary='merlot.ProjectStatusVocabulary',
        default=u'In progress',
    )
    # chronic = schema.Bool(title=u'Chronic', required=True)
    start_date = schema.Date(
        title=_(u'Start date'),
        required=True,
    )
    end_date = schema.Date(title=_(u'End date'), required=False)

    @invariant
    def startBeforeEnd(project):
        """Check that the start date is prior to the end date"""
        if project.end_date and project.start_date:
            if project.end_date < project.start_date:
                raise Invalid(_('Start date must preceed end date'))


class ITask(Interface):
    """A simple task"""

    next_id = schema.Int(title=_(u'Next ID'), default=1)
    """The next ID to be used for the contained log objects.

    Tasks will contain logs. Logs inside a task will have IDs
    following the serie '1', '2', '3' and so on. This attribute stores
    the ID to be used for the next log object to be added inside the
    task.
    """

    title = schema.TextLine(title=_(u'Title'), required=True)
    description = schema.Text(title=_(u'Description'), required=False)
    priority = schema.Choice(
        title=_(u'Priority'),
        required=True,
        vocabulary='merlot.TaskPriorityVocabulary',
        default=u'Normal',
    )
    status = schema.Choice(
        title=_(u'Status'),
        required=True,
        description=_(u'The status the task is in'),
        vocabulary='merlot.ProjectStatusVocabulary',
        default=u'In progress',
    )
    start_date = schema.Date(
        title=_(u'Start date'),
        required=True,
    )
    end_date = schema.Date(title=_(u'End date'), required=False)
    estimate = schema.Decimal(title=_(u'Hours estimate'), required=False)
    remaining = schema.Decimal(title=_(u'Remaining hours'), required=False)

    def deleteFromStarredLists():
        """Remove the task from the starred tasks lists"""

    @invariant
    def startBeforeEnd(task):
        """Check that the start date is prior to the end date"""
        if task.end_date and task.start_date:
            if task.end_date < task.start_date:
                raise Invalid(_('Start date must preceed end date'))


class ILog(Interface):
    """A time log object"""
    description = schema.Text(title=_(u'Description'), required=True)
    date = schema.Date(
        title=_(u'Date'),
        required=True,
    )
    user = schema.BytesLine(title=_(u'Username'), required=True)
    hours = schema.Decimal(title=_(u'Worked hours'), required=True)
    remaining = schema.Decimal(
        title=_(u'Remaining hours'),
        description=_(u'The task will be automatically marked as completed if '
                       'you enter 0 here'),
        required=False)


# Stats adapters
class ITaskStats(Interface):
    """Task statistics"""

    def getWorkedHours():
        """The total amount of hours logged in the task"""

    def getUserWorkedHours():
        """The total amount of hours logged in the task by the
        authenticated user.
        """


class IProjectStats(Interface):
    """Project statistics"""

    def getWorkedHours():
        """The total amount of hours logged in the project"""

    def getUserWorkedHours():
        """The total amount of hours logged in the prject by the
        authenticated user.
        """


class IClientContainer(Interface):
    """A container for client objects"""
    next_id = schema.Int(title=_(u'Next ID'), default=1)
    title = schema.TextLine(title=_(u'Title'), required=True)


class IClient(Interface):
    """A client object"""
    title = schema.TextLine(title=_(u'Title'), required=True)
    type = schema.Choice(
        title=_(u'Type'),
        required=False,
        description=_(u'The client type'),
        vocabulary='merlot.ClientTypeVocabulary',
        default=u'company',
    )


class ISearchable(Interface):
    """The attributes and methods in this interface represent catalog
    indexes.
    """
    title = Attribute('title')
    description = Attribute('description')
    start_date = Attribute('start_date')
    end_date = Attribute('end_date')
    client = Attribute('client')
    modification_date = Attribute('modification_date')
    user = Attribute('user')
    content_type = Attribute('content_type')
    status = Attribute('status')
    date = Attribute('date')

    def searchable_text():
        """Concatenation of all text fields to search"""

    def task():
        """The task a log is in"""

    def project():
        """The project a task or a log is in"""


class ILogsReport(Interface):
    """The logs report form"""
    project_or_client = schema.Choice(
        title=_(u'Project'),
        description=_('Select a project'),
        required=True,
        vocabulary='merlot.ProjectVocabulary',
        default=u'All projects',
    )
    from_date = schema.Date(
        title=_(u'From'),
        required=True
    )
    to_date = schema.Date(
        title=_(u'To'),
        required=True,
    )
    user = schema.Choice(
        title=_(u'User'),
        description=_('Select a user'),
        required=True,
        vocabulary='merlot.UserVocabulary',
        default='All users',
    )


class ITasksReport(Interface):
    """The tasks report form"""
    projects = schema.Choice(
        title=_(u'Project'),
        description=_('Select a project'),
        required=True,
        vocabulary='merlot.ProjectVocabulary',
        default=u'All projects',
    )
    from_date = schema.Date(
        title=_(u'From'),
        required=True
    )
    to_date = schema.Date(
        title=_(u'To'),
        required=True,
    )
    user = schema.Choice(
        title=_(u'User'),
        description=_('Select a user'),
        required=True,
        vocabulary='merlot.UserVocabulary',
        default='All users',
    )


class IStarredTasks(Interface):
    """A list of starred tasks per user"""

    def getStarredTasks():
        """Return a list of starred tasks for the adapted user account"""

    def addStarredTask(task_intid):
        """Add a task to the starred tasks list"""

    def removeStarredTask(task_intid):
        """Remove a task from the starred tasks list"""
