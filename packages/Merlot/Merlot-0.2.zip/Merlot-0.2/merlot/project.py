"""This module implements models and views for a simple project.

A project can contain tasks, which in turn can contain logs.
"""

import datetime
import json
from BTrees.OOBTree import OOSet
import grok
import grok.index

from zope.publisher.interfaces import IRequest
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, getUtility
from zope.intid.interfaces import IIntIds
from zope.catalog.interfaces import ICatalog
from zope.app.authentication.interfaces import IAuthenticatorPlugin

from z3c.relationfield.interfaces import IHasOutgoingRelations

import merlot.interfaces as ifaces
from merlot.lib import normalize, master_template, default_form_template, \
    DATE_FORMAT
from merlot import MerlotMessageFactory as _


class ProjectContainer(grok.Container):
    grok.implements(ifaces.IProjectContainer)

    def __init__(self, title=None):
        super(ProjectContainer, self).__init__()
        if title:
            self.title = title


class ProjectContainerIndex(grok.View):
    """The project container view"""
    grok.context(ifaces.IProjectContainer)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template

    def update(self):
        self.projects = [i for i in self.context if \
            ifaces.IProject.providedBy(self.context[i])]


class ProjectContainerListing(grok.View):
    grok.context(ifaces.IProjectContainer)
    grok.name('projects_listing')
    grok.require('merlot.Manage')
    grok.template('projects_listing')
    grok.order(1)

    def update(self):
        query = {'content_type': ('Project', 'Project')}
        status = self.request.get('status', None)
        if status:
            query['status'] = (status, status)
        catalog = getUtility(ICatalog)
        self.projects = catalog.searchResults(**query)
        return


class ProjectContainerIndexViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IProjectContainer)
    grok.template('projectcontainer_index')
    grok.view(ProjectContainerIndex)
    grok.order(10)

    def update(self):
        statuses = getUtility(IVocabularyFactory,
                              name='merlot.ProjectStatusVocabulary')
        self.statuses = statuses().by_token.values()


class Project(grok.Container):
    """The simple project model"""
    grok.implements(ifaces.IProject, ifaces.IMetadata, ifaces.ISearchable,
                    IHasOutgoingRelations)
    content_type = 'Project'

    def __init__(self):
        super(Project, self).__init__()
        self.title = u''
        self.description = u''

    def searchable_text(self):
        result = ''
        if self.title:
            result += self.title
        if self.description:
            result += self.description
        return result


# Project catalog indexes
class CatalogIndexes(grok.Indexes):
    """The catalog indexes of the application"""
    grok.site(ifaces.IMerlot)
    grok.context(ifaces.ISearchable)

    title = grok.index.Text()
    description = grok.index.Text()
    searchable_text = grok.index.Text()
    modification_date = grok.index.Field()
    start_date = grok.index.Field()
    end_date = grok.index.Field()
    #client = grok.index.Field()
    user = grok.index.Field()
    content_type = grok.index.Field()
    status = grok.index.Field()
    task = grok.index.Field()
    project = grok.index.Field()
    date = grok.index.Field()


# The add project form, view and viewlet
class AddProjectForm(grok.AddForm):
    """The add project form"""
    grok.context(ifaces.IProjectContainer)
    grok.name('add-project-form')
    grok.require('merlot.Manage')
    form_fields = grok.AutoFields(ifaces.IProject)
    label = _(u'Create a new project')
    template = default_form_template

    @grok.action(_(u'Add project'))
    def add(self, **data):
        """Add a project"""
        project = Project()
        project.creator = self.request.principal.title
        project.creation_date = datetime.datetime.now()
        project.modification_date = datetime.datetime.now()
        self.applyData(project, **data)

        title = data['title']
        suffix = 1
        id = normalize(title)
        while id in self.context:
            title += str(suffix)
            suffix += 1
            id = normalize(title)

        project.id = id
        self.context[id] = project
        self.flash(_(u'Project added.'), type=u'message')
        return self.redirect(self.url(self.context[id]))

    def setUpWidgets(self, ignore_request=False):
        super(AddProjectForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50
        self.widgets['description'].height = 5
        self.widgets['start_date']._data = \
            datetime.datetime.now().strftime(DATE_FORMAT)


class AddProject(grok.View):
    """The add project view"""
    grok.context(ifaces.IProjectContainer)
    grok.name('add-project')
    grok.require('merlot.Manage')
    template = master_template


class AddProjectViewlet(grok.Viewlet):
    """The add project viewlet, which renders the add project form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(AddProject)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='add-project-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


# The edit project form, view and viewlet
class EditProjectForm(grok.EditForm):
    """Edit project form"""
    grok.context(ifaces.IProject)
    grok.name('edit-form')
    form_fields = grok.AutoFields(ifaces.IProject)
    label = _('Edit the project')
    template = default_form_template

    def setUpWidgets(self, ignore_request=False):
        super(EditProjectForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50
        self.widgets['description'].height = 5

    @grok.action(_('Save'))
    def edit(self, **data):
        """Make the changes persistent"""
        self.context.modification_date = datetime.datetime.now()
        self.applyData(self.context, **data)
        self.flash(_(u'Changes saved.'), type=u'message')
        return self.redirect(self.url(self.context))


class EditProject(grok.View):
    """The edit project view"""
    grok.context(ifaces.IProject)
    grok.name('edit')
    grok.require('merlot.Manage')
    template = master_template


class EditProjectViewlet(grok.Viewlet):
    """The edit project viewlet, which renders the edit project form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IProject)
    grok.view(EditProject)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='edit-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class ProjectIndex(grok.View):
    """The project view"""
    grok.context(ifaces.IProject)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template


class ProjectIndexViewlet(grok.Viewlet):
    """The project view main viewlet"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IProject)
    grok.template('project_index')
    grok.view(ProjectIndex)
    grok.order(10)

    def update(self):
        self.stats = getMultiAdapter((self.context, self.request),
                                     ifaces.IProjectStats)

        # Build a list of starred tasks for the authenticated user
        self.starred_tasks = []
        users = getUtility(IAuthenticatorPlugin, 'users')
        intids = getUtility(IIntIds, name='intids')
        user = users.getAccount(self.request.principal.id)

        if user:
            starred_tasks = ifaces.IStarredTasks(user)
            for task_intid in starred_tasks.getStarredTasks():
                task = intids.getObject(task_intid)
                self.starred_tasks.append(task)

        self.tasks_stats = {}
        for i in self.context:
            self.tasks_stats[i] = getMultiAdapter((self.context[i],
                                                   self.request),
                                                  ifaces.ITaskStats)

        # Build a list of tasks ordered by priority and creation date
        ordered_tasks = []
        priorities_vocab = getUtility(IVocabularyFactory,
                                      name='merlot.TaskPriorityVocabulary')
        priorities = [p for (p, k, v) in priorities_vocab.terms]
        for priority in priorities:
            tasks = [t for t in self.context.values() if \
                     t.priority == priority]
            tasks = sorted(tasks, key=lambda t: t.creation_date)
            ordered_tasks += tasks

        tasks = [t for t in self.context.values() if t.priority == None]
        ordered_tasks += tasks

        self.tasks = ordered_tasks


class DeleteProject(grok.View):
    """Delete the project and return to the dashboard"""

    grok.context(ifaces.IProject)
    grok.name('delete')
    grok.require('merlot.Manage')

    def render(self):
        project_container = self.context.__parent__

        # Delete the contained tasks from the user starred lists
        for task in self.context.values():
            if ifaces.ITask.providedBy(task):
                task.deleteFromStarredLists()

        del project_container[self.context.id]
        self.flash(_(u'Project deleted.'), type=u'message')
        return self.redirect(self.url(project_container))


# Tasks
class Task(grok.Container):
    """The task model"""
    grok.implements(ifaces.ITask, ifaces.IMetadata, ifaces.ISearchable)
    content_type = 'Task'

    def __init__(self):
        super(Task, self).__init__()
        self.next_id = 1

    def searchable_text(self):
        result = ''
        if self.title:
            result += self.title
        if self.description:
            result += self.description
        return result

    def project(self):
        """Returns the intid of the parent project"""
        intids = getUtility(IIntIds, name='intids')
        project = self.__parent__
        intid = intids.getId(project)
        return intid

    def deleteFromStarredLists(self):
        """Remove the task from the starred tasks lists"""
        app = grok.getSite()
        intids = getUtility(IIntIds, name='intids')

        for user in app['users'].values():
            starred_tasks = ifaces.IStarredTasks(user)
            intid = intids.getId(self)
            starred_tasks.removeStarredTask(intid)


# The add task form, view and viewlet
class AddTaskForm(grok.AddForm):
    """The add task form"""
    grok.context(ifaces.IProject)
    grok.name('add-task-form')
    form_fields = grok.AutoFields(ifaces.ITask).omit('next_id', 'remaining')
    label = _('Create a new task')
    template = default_form_template

    @grok.action(_('Add task'))
    def add(self, **data):
        """Add a task inside the current project"""
        task = Task()
        task.creator = self.request.principal.title
        task.creation_date = datetime.datetime.now()
        task.modification_date = datetime.datetime.now()
        task.remaining = data['estimate']
        self.applyData(task, **data)

        title = data['title']
        suffix = 1
        id = normalize(title)
        while id in self.context:
            title += str(suffix)
            suffix += 1
            id = normalize(title)

        task.id = id
        self.context[id] = task
        self.flash(_(u'Task added.'), type=u'message')
        return self.redirect(self.url(self.context))

    def setUpWidgets(self, ignore_request=False):
        super(AddTaskForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50
        self.widgets['description'].height = 5
        self.widgets['start_date']._data = \
            datetime.datetime.now().strftime(DATE_FORMAT)


class AddTask(grok.View):
    """The add task view"""
    grok.context(ifaces.IProject)
    grok.name('add-task')
    grok.require('merlot.Manage')
    template = master_template


class AddTaskViewlet(grok.Viewlet):
    """The add task viewlet, which renders the add task form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(AddTask)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='add-task-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


# The edit task form, view and viewlet
class EditTaskForm(grok.EditForm):
    """The edit task form"""
    grok.context(ifaces.ITask)
    grok.name('edit-form')
    form_fields = grok.AutoFields(ifaces.ITask).omit('next_id')
    label = _('Edit the task')
    template = default_form_template

    def setUpWidgets(self, ignore_request=False):
        super(EditTaskForm, self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 50
        self.widgets['description'].height = 5

    @grok.action('Save')
    def edit(self, **data):
        """Update the task attributes"""
        self.context.modification_date = datetime.datetime.now()
        self.applyData(self.context, **data)
        self.flash(_(u'Changes saved.'), type=u'message')
        return self.redirect(self.url(self.context))


class EditTask(grok.View):
    """The edit task view"""
    grok.context(ifaces.ITask)
    grok.name('edit')
    grok.require('merlot.Manage')
    template = master_template


class EditTaskViewlet(grok.Viewlet):
    """The edit task viewlet, which renders the edit task form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.ITask)
    grok.view(EditTask)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='edit-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class TaskIndex(grok.View):
    """The task view"""
    grok.context(ifaces.ITask)
    grok.name('index')
    grok.require('merlot.Manage')
    template = master_template


class TaskIndexViewlet(grok.Viewlet):
    """The task view main viewlet"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.ITask)
    grok.template('task_index')
    grok.view(TaskIndex)
    grok.order(10)

    def update(self):
        # XXX: this is ineficient
        xl = list(self.context.values())
        xl.sort(key=lambda x: x.date)
        self.logs = xl

        self.stats = getMultiAdapter((self.context, self.request),
                                     ifaces.ITaskStats)

    def starred(self):
        starred_tasks = []
        users = getUtility(IAuthenticatorPlugin, 'users')
        intids = getUtility(IIntIds, name='intids')
        user = users.getAccount(self.request.principal.id)

        result = False
        if user:
            starred_tasks = ifaces.IStarredTasks(user)

            starred_tasks_obj = map(intids.getObject,
                                    starred_tasks.getStarredTasks())

            if self.context in starred_tasks_obj:
                result = True

        return result


class DeleteTask(grok.View):
    """Delete the task and return to the project view"""
    grok.context(ifaces.ITask)
    grok.name('delete')
    grok.require('merlot.Manage')

    def render(self):
        project = self.context.__parent__
        self.context.deleteFromStarredLists()
        del project[self.context.id]
        self.flash(_(u'Task deleted.'), type=u'message')
        return self.redirect(self.url(project))


# Logs
class Log(grok.Model):
    """The log type"""
    grok.implements(ifaces.ILog, ifaces.IMetadata, ifaces.ISearchable)
    content_type = 'Log'

    def task(self):
        """The intid of the task where the log belongs to"""
        intids = getUtility(IIntIds, name='intids')
        task = self.__parent__
        intid = intids.getId(task)
        return intid

    def project(self):
        """The intid of the project where the log belongs to"""
        intids = getUtility(IIntIds, name='intids')
        project = self.__parent__.__parent__
        intid = intids.getId(project)
        return intid


# The add log form
class AddLogForm(grok.AddForm):
    """The add log form"""
    grok.context(ifaces.ITask)
    grok.name('add-log-form')
    grok.require('merlot.Manage')
    form_fields = grok.AutoFields(ifaces.ILog).omit('user')
    #label = 'Create a new log'
    template = default_form_template

    @grok.action(_('Add log'))
    def add(self, **data):
        """Add a log inside the current task"""
        log = Log()
        log.creator = self.request.principal.title
        log.creation_date = datetime.datetime.now()
        log.modification_date = datetime.datetime.now()
        log.user = self.request.principal.id
        self.applyData(log, **data)

        id = str(self.context.next_id)
        log.id = id
        self.context.next_id = self.context.next_id + 1
        self.context[id] = log
        if data['remaining'] is not None:
            if data['remaining'] == 0:
                self.context.status = u'Completed'
            self.context.remaining = data['remaining']

        self.flash(_(u'Log added.'), type=u'message')
        return self.redirect(self.url(self.context))

    def setUpWidgets(self, ignore_request=False):
        super(AddLogForm, self).setUpWidgets(ignore_request)
        self.widgets['description'].height = 5
        #XXX: I'm using a private method.. bad boy, bad boy...
        self.widgets['remaining']._data = self.context.remaining
        self.widgets['date']._data = \
            datetime.datetime.now().strftime(DATE_FORMAT)


# XXX this is a DIRTY way of do ajax, the logic is the same that we can
# find in the method AddLogForm, sadly I didn't find a way to set the
# name in the generated form for the submit buttons. in the form bellow
# the name is going to be: form.actions.<some large number>
class AddLogAjax(grok.AddForm):
    grok.context(ifaces.ITask)
    grok.name('add-log-ajax')
    grok.require('merlot.Manage')
    form_fields = grok.AutoFields(ifaces.ILog).omit('user')
    template = grok.PageTemplateFile('project_templates/add_log_ajax_form.pt')

    @grok.action(_(u'Log'))
    def save(self, **data):
        """Add a log inside the current task"""
        log = Log()
        log.creator = self.request.principal.title
        log.creation_date = datetime.datetime.now()
        log.modification_date = datetime.datetime.now()
        log.user = self.request.principal.id
        self.applyData(log, **data)

        id = str(self.context.next_id)
        log.id = id
        self.context.next_id = self.context.next_id + 1
        self.context[id] = log
        if data['remaining'] is not None:
            if data['remaining'] == 0:
                self.context.status = u'Completed'
            self.context.remaining = data['remaining']

        #btw in IE and chrome this is not going to work because they NEED
        # the header defined, this is my official boicot to them.
        json_result = {}
        json_result['hours'] = str(log.hours)
        json_result['remaining'] = str(log.remaining)
        json_result['date'] = log.date.strftime('%d - %m - %Y')
        result = json.dumps(json_result)
        return result

    def setUpWidgets(self, ignore_request=False):
        super(AddLogAjax, self).setUpWidgets(ignore_request)
        #XXX i'm using a private method.. bad boy bad boy...
        self.widgets['remaining'].displayWidth = 3
        self.widgets['remaining']._data = self.context.remaining


class AddLogViewlet(grok.Viewlet):
    """The add log viewlet, which renders the add log form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.ITask)
    grok.view(TaskIndex)
    grok.order(11)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='add-log-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


# The edit log form, view and viewlet
class EditLogForm(grok.EditForm):
    """The edit log form"""
    grok.context(ifaces.ILog)
    grok.name('edit-form')
    form_fields = grok.AutoFields(ifaces.ILog).omit('user', 'remaining')
    label = 'Edit the log'
    template = default_form_template

    def setUpWidgets(self, ignore_request=False):
        super(EditLogForm, self).setUpWidgets(ignore_request)
        self.widgets['description'].height = 5

    @grok.action('Save')
    def edit(self, **data):
        """Make the changes persistent"""
        self.context.modification_date = datetime.datetime.now()
        self.applyData(self.context, **data)
        self.flash(_(u'Changes saved.'), type=u'message')
        return self.redirect(self.url(self.context.__parent__))


class EditLog(grok.View):
    """The edit log view"""
    grok.context(ifaces.ILog)
    grok.name('edit')
    grok.require('merlot.Manage')
    template = master_template


class EditLogViewlet(grok.Viewlet):
    """The edit log viewlet, which renders the edit log form"""
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.ILog)
    grok.view(EditLog)
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='edit-form')
        self.form.update_form()

    def render(self):
        return self.form.render()


class DeleteLog(grok.View):
    """Delete the log and return to the task"""

    grok.context(ifaces.ILog)
    grok.name('delete')
    grok.require('merlot.Manage')

    def render(self):
        task = self.context.__parent__
        del task[self.context.id]
        self.flash(_(u'Log deleted.'), type=u'message')
        return self.redirect(self.url(task))


# Task and project stats adapters
class TaskStats(grok.MultiAdapter):
    """Task stats adapter.

    It gives information about the amount of hours worked in a task in
    total and by the authenticated user.
    """
    grok.adapts(ifaces.ITask, IRequest)
    grok.implements(ifaces.ITaskStats)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getWorkedHours(self):
        """Total worked hours in the task"""
        hours = 0
        for log in self.context:
            hours += self.context[log].hours

        return hours

    def getUserWorkedHours(self):
        """Hours worked by the authenticated user in the adapted task"""
        hours = 0
        for log in self.context:
            if self.context[log].user == self.request.principal.id:
                hours += self.context[log].hours

        return hours


class ProjectStats(grok.MultiAdapter):
    """Project stats adapter.

    It gives information about the amount of hours worked in a project
    in total and by the authenticated user.
    """

    grok.adapts(ifaces.IProject, IRequest)
    grok.implements(ifaces.IProjectStats)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getWorkedHours(self):
        """Total worked hours in the project"""
        hours = 0
        for task in self.context:
            obj = self.context[task]
            hours += getMultiAdapter((obj, self.request),
                                     ifaces.ITaskStats).getWorkedHours()

        return hours

    def getUserWorkedHours(self):
        """Hours worked by the authenticated user in the adapted
        project.
        """
        hours = 0
        for task in self.context:
            obj = self.context[task]
            hours += getMultiAdapter((obj, self.request),
                                     ifaces.ITaskStats).getUserWorkedHours()

        return hours


class StarredTasks(grok.Annotation):
    grok.context(ifaces.IAccount)
    grok.implements(ifaces.IStarredTasks)

    def __init__(self):
        self._starred_tasks = OOSet()

    def getStarredTasks(self):
        return list(self._starred_tasks)

    def addStarredTask(self, task_intid):
        self._starred_tasks.insert(task_intid)

    def removeStarredTask(self, task_intid):
        if task_intid in self._starred_tasks:
            self._starred_tasks.remove(task_intid)


class ToggleStarredTask(grok.View):
    grok.context(ifaces.ITask)
    grok.name('toggle-starred')
    grok.require('merlot.Manage')

    def render(self):
        users = getUtility(IAuthenticatorPlugin, 'users')
        intids = getUtility(IIntIds, name='intids')

        user = users.getAccount(self.request.principal.id)
        intid = intids.getId(self.context)

        starred_tasks = ifaces.IStarredTasks(user)

        if intid in starred_tasks.getStarredTasks():
            starred_tasks.removeStarredTask(intid)
            msg = _("You've removed the star from the task")
        else:
            starred_tasks.addStarredTask(intid)
            msg = _("You've marked the task with a star")

        self.flash(msg, type=u'message')
        url = self.request.get('camefrom', self.url(self.context))
        return self.redirect(url)
