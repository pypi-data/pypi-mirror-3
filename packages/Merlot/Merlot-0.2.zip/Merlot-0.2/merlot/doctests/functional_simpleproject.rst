Simple Project Functional Tests
-------------------------------

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer

We need to create a user to play with later. First of all we access the site
as admin::

    >>> from zope.app.wsgi.testlayer import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic admin:admin')
    >>> browser.open('http://localhost/app')
    >>> 'Logged in as: Manager' in browser.contents
    True

Now we create a new user::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('Add new User').click()
    >>> browser.getControl(name="form.id").value = u'user'
    >>> browser.getControl(name="form.real_name").value = u'Testing User'
    >>> browser.getControl(name="form.password").value = u'secret'
    >>> browser.getControl(name="form.confirm_password").value = u'secret'
    >>> browser.getControl("Add user").click()
    >>> 'User added' in browser.contents
    True
    >>> 'Testing User' in browser.contents
    True

We are now ready to start testing projects. Let's log in with the user we've
just created::

    >>> browser = Browser()
    >>> browser.open('http://localhost/app')
    >>> browser.getControl(name="form.username").value = u'user'
    >>> browser.getControl(name="form.password").value = u'secret'
    >>> browser.getControl("Login").click()
    >>> 'You are logged in.' in browser.contents
    True

Since we must associate projects to clients, let's start by creating a client::

    >>> browser.getLink('Clients').click()
    >>> browser.getLink('Add new Client').click()
    >>> browser.getControl(name="form.title").value = u'Acme'
    >>> browser.getControl("Add client").click()
    >>> 'Client added' in browser.contents
    True

Now we can create a project. Let's try to submit the add project form after
filling just the title and check that we get proper validation errors to fill
required fields::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Develop a web app'
    >>> browser.getControl("Add project").click()
    >>> 'Required input is missing' in browser.contents
    True

The project status defaults to In progress::

    >>> browser.getControl(name='form.status').value
    ['In progress']

Also, the start date is automatically set to today::

    >>> from datetime import datetime, timedelta
    >>> from merlot.lib import DATE_FORMAT
    >>> today = datetime.today().strftime(DATE_FORMAT)
    >>> browser.getControl(name='form.start_date').value == today
    True

If we try to set an end date prior to the start date, we will also get a
validation error::

    >>> yesterday = datetime.today() - timedelta(1)
    >>> yesterday = yesterday.strftime(DATE_FORMAT)
    >>> browser.getControl(name='form.end_date').value = yesterday
    >>> browser.getControl("Add project").click()
    >>> 'Start date must preceed end date' in browser.contents
    True

So let's set the end date to tomorrow and fill the client field to finally add
the project::

    >>> tomorrow = datetime.today() + timedelta(1)
    >>> tomorrow = tomorrow.strftime(DATE_FORMAT)
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl("Add project").click()
    >>> 'Project added' in browser.contents
    True

And we were redirected to the created project view. Notice how the URL was
generated based on the title we used::

    >>> browser.url
    'http://localhost/app/projects/develop-a-web-app'
    >>> 'Project view: Develop a web app' in browser.contents
    True

Projects can contain tasks, so let's create a task, but first let's verify that
the `priority` field defaults to `Normal`, that the `status` field defaults to
`In progress` and that `start_date` default to the current date::

    >>> browser.getLink('Add new Task').click()
    >>> browser.getControl(name='form.priority').value
    ['Normal']
    >>> browser.getControl(name='form.status').value
    ['In progress']
    >>> browser.getControl(name='form.start_date').value == today
    True

No we will fill some fields and submit the form. Once again, if we set an end
date prior to the start date, we get a validation error::

    >>> browser.getControl(name="form.title").value = u'Define requirements'
    >>> browser.getControl(name='form.end_date').value = yesterday
    >>> browser.getControl("Add task").click()
    >>> 'Start date must preceed end date' in browser.contents
    True

Let's set the end date to tomorrow and add the task::

    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl("Add task").click()
    >>> 'Task added' in browser.contents
    True

We are still in the project view::

    >>> browser.url
    'http://localhost/app/projects/develop-a-web-app'
    >>> 'Project view: Develop a web app' in browser.contents
    True

Let's quickly add another task::

    >>> browser.getLink('Add new Task').click()
    >>> browser.getControl(name="form.title").value = u'Testing'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl("Add task").click()
    >>> 'Task added' in browser.contents
    True

We can delete a task from the project view::

    >>> browser.getLink('delete', index=2).click()
    >>> 'Are you sure you want to delete the "Testing" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Task deleted.' in browser.contents
    True

And we are still in the project view::

    >>> browser.url
    'http://localhost/app/projects/develop-a-web-app'
    >>> 'Project view: Develop a web app' in browser.contents
    True

In order to track the time that a task takes, you can associate time logs to
them. Let's go the the task view, and there we can add a log::

    >>> browser.getLink('Define requirements').click()
    >>> 'Task view: Define requirements' in browser.contents
    True
    >>> browser.getControl(name='form.description').value = u'Write document'
    >>> browser.getControl(name='form.date').value == today
    True
    >>> browser.getControl(name='form.hours').value = u'6'
    >>> browser.getControl(name='form.remaining').value = u'2.4'
    >>> browser.getControl('Add log').click()
    >>> 'Log added' in browser.contents
    True
    >>> 'Write document' in browser.contents
    True

We are still in the task view::

    >>> 'Task view: Define requirements' in browser.contents
    True

The remaining hours set when adding a log updates the remaining hours field in
the task::

    >>> from decimal import Decimal
    >>> task = app['projects']['develop-a-web-app']['define-requirements']
    >>> task.remaining == Decimal('2.4')
    True

Let's check that there are some required fields to add a log by submitting the
form without filling any field::

    >>> browser.getControl('Add log').click()
    >>> 'Required input is missing' in browser.contents
    True

Let's mark the current task as starred, but before, let's check what are the
current starred tasks for the authenticated user::

    >>> from merlot.interfaces import IStarredTasks
    >>> from zope.component import getUtility
    >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
    >>> from zope.intid.interfaces import IIntIds
    >>> user = app['users']['user']
    >>> starred_tasks = IStarredTasks(user)
    >>> starred_tasks.getStarredTasks()
    []

Now we mark the task as starred::

    >>> browser.getLink(url=('http://localhost/app/projects/develop-a-web-app/'
    ...                      'define-requirements/toggle-starred')).click()

Now the task is marked as starred for the current user::

    >>> intids = getUtility(IIntIds, name='intids', context=app)
    >>> intid = intids.getId(task)
    >>> starred_tasks.getStarredTasks() == [intid]
    True

    >>> link = browser.getLink(url=('http://localhost/app/projects/'
    ...                             'develop-a-web-app/define-requirements/'
    ...                             'toggle-starred'))
    >>> link.attrs['class'] == 'starred-selected'
    True

Let's quickly create another task and mark it as starred::

    >>> browser.getLink('Develop a web app').click()
    >>> browser.getLink('Add new Task').click()
    >>> browser.getControl(name="form.title").value = u'New task'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl("Add task").click()
    >>> 'Task added' in browser.contents
    True
    >>> browser.getLink('New task').click()
    >>> browser.getLink(url=('http://localhost/app/projects/develop-a-web-app/'
    ...                      'new-task/toggle-starred')).click()

Let's check that it is actually marked as starred for the authenticated user::

    >>> newtask = app['projects']['develop-a-web-app']['new-task']
    >>> newtask_intid = intids.getId(newtask)
    >>> starred_tasks.getStarredTasks() == [intid, newtask_intid]
    True

Let's now edit the first task and change the hours estimate to 10::

    >>> browser.getLink('Develop a web app').click()
    >>> browser.getLink('Define requirements').click()
    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='form.estimate').value = '10'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

The changes persisted::

    >>> task.estimate == Decimal(10)
    True

Logs can also be edited::

    >>> browser.getLink('edit', index=1).click()
    >>> browser.getControl(name='form.description').value = 'New description'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> 'New description' in browser.contents
    True
    >>> 'Write document' in browser.contents
    False

If a task is deleted, it will be automatically removed from all users' starred
tasks lists. Lets delete one of the tasks and check that it's also removed
from the starred tasks list of the authenticated user::

    >>> browser.getLink('Delete').click()
    >>> 'Are you sure you want to delete the "Define requirements" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Task deleted' in browser.contents
    True
    >>> starred_tasks.getStarredTasks() == [newtask_intid]
    True

Moreover, if we delete the project that contains an starred task, then that
task is also removed from all users' starred tasks lists. Let's delete the
project and test this::

    >>> browser.getLink('Delete').click()
    >>> 'Are you sure you want to delete the "Develop a web app" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Project deleted' in browser.contents
    True
    >>> starred_tasks.getStarredTasks()
    []

Let's now create a new project::

    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Project'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl("Add project").click()
    >>> 'Project added' in browser.contents
    True

Let's create another project with the same title and check that the IDs don't
clash::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Project'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl("Add project").click()
    >>> 'Project added' in browser.contents
    True
    >>> browser.url
    'http://localhost/app/projects/project1'

Let's edit the current project by changing the title and start date::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name="form.title").value = u'Project 2'
    >>> browser.getControl(name='form.start_date').value = yesterday
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.url
    'http://localhost/app/projects/project1'

And let's check that the changes persisted::

    >>> project1 = app['projects']['project1']
    >>> project1.title
    u'Project 2'
    >>> project1.start_date == datetime.today().date() - timedelta(1)
    True
    
