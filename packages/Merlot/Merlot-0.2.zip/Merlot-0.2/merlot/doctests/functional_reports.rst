Reports Functional Tests
------------------------

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer

There are currently two reports available, a `Logs report` and a `Tasks
report`. Read on to learn about what those are about.

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

Let's log in with the user we've just created::

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

Let's now create two new projects, but first let's set some formatted strings
with dates::

    >>> from datetime import datetime, timedelta
    >>> from merlot.lib import DATE_FORMAT
    >>> today = datetime.today().strftime(DATE_FORMAT)
    >>> yesterday = datetime.today() - timedelta(1)
    >>> yesterday = yesterday.strftime(DATE_FORMAT)
    >>> tomorrow = datetime.today() + timedelta(1)
    >>> tomorrow = tomorrow.strftime(DATE_FORMAT)

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Project One'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl("Add project").click()
    >>> 'Project added' in browser.contents
    True

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Project Two'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl("Add project").click()
    >>> 'Project added' in browser.contents
    True

Let's create one task in each of the projects we created. We create a task in
`Project Two`::

    >>> browser.getLink('Add new Task').click()
    >>> browser.getControl(name='form.start_date').value == today
    True
    >>> browser.getControl(name="form.title").value = u'Define requirements'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl("Add task").click()
    >>> 'Task added' in browser.contents
    True

And we also create a task in `Project One`::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Project One').click()
    >>> browser.getLink('Add new Task').click()
    >>> browser.getControl(name="form.title").value = u'A simple task'
    >>> browser.getControl(name='form.end_date').value = tomorrow
    >>> browser.getControl("Add task").click()
    >>> 'Task added' in browser.contents
    True

Let's now log some time in both tasks. First we add a couple of logs in the
task we've just created::

    >>> browser.getLink('A simple task').click()
    >>> 'Task view: A simple task' in browser.contents
    True
    >>> browser.getControl(name='form.description').value = u'Write document'
    >>> browser.getControl(name='form.date').value = yesterday
    >>> browser.getControl(name='form.hours').value = u'6'
    >>> browser.getControl(name='form.remaining').value = u'2.4'
    >>> browser.getControl('Add log').click()
    >>> 'Log added' in browser.contents
    True
    >>> browser.getControl(name='form.description').value = u'Close this task'
    >>> browser.getControl(name='form.date').value = today
    >>> browser.getControl(name='form.hours').value = u'3'
    >>> browser.getControl(name='form.remaining').value = u'0'
    >>> browser.getControl('Add log').click()
    >>> 'Log added' in browser.contents
    True

And now we add a couple of logs in the task we created for `Project Two`::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Project Two').click()
    >>> browser.getLink('Define requirements').click()
    >>> 'Task view: Define requirements' in browser.contents
    True
    >>> browser.getControl(name='form.description').value = u'Meeting with Joe'
    >>> browser.getControl(name='form.hours').value = u'4'
    >>> browser.getControl(name='form.remaining').value = u'2'
    >>> browser.getControl('Add log').click()
    >>> 'Log added' in browser.contents
    True
    >>> browser.getControl(name='form.description').value = u'Finish document'
    >>> browser.getControl(name='form.hours').value = u'3'
    >>> browser.getControl(name='form.date').value = tomorrow
    >>> browser.getControl(name='form.remaining').value = u'0'
    >>> browser.getControl('Add log').click()
    >>> 'Log added' in browser.contents
    True

We are now ready to run the `Logs report`. This report queries the log entries
in a range of dates filtering by project and user. The results are presented in
a flat table.

So, to get to the report screen, we click on the `Reports` tab and then on the
`Logs report` link::

    >>> browser.getLink('Reports').click()
    >>> browser.getLink('Logs report').click()
    >>> 'Run logs report' in browser.contents
    True

The `from` and `to` dates are set to today::

    >>> browser.getControl(name='form.from_date').value == today
    True
    >>> browser.getControl(name='form.to_date').value == today
    True

All users and all projects are selected by default::

    >>> browser.getControl(name='form.project_or_client').value
    ['all']
    >>> browser.getControl(name='form.user').value
    ['all']

So, if we run the report with those options, we should get only today's logs::

    >>> browser.getControl('Submit').click()
    >>> 'Write document' in browser.contents
    False
    >>> 'Close this task' in browser.contents
    True
    >>> 'Meeting with Joe' in browser.contents
    True
    >>> 'Finish document' in browser.contents
    False

If we set the `from` date to yesterday, we will also get yesterday's logs::

    >>> browser.getControl(name='form.from_date').value = yesterday
    >>> browser.getControl('Submit').click()
    >>> 'Write document' in browser.contents
    True
    >>> 'Close this task' in browser.contents
    True
    >>> 'Meeting with Joe' in browser.contents
    True
    >>> 'Finish document' in browser.contents
    False

If we rescrict the report to `Project One`::

    >>> browser.getControl(name='form.project_or_client').value = \
    ...     ('/app/projects/project-one',)
    >>> browser.getControl('Submit').click()
    >>> 'Write document' in browser.contents
    True
    >>> 'Close this task' in browser.contents
    True
    >>> 'Meeting with Joe' in browser.contents
    False
    >>> 'Finish document' in browser.contents
    False

The report can be downloaded in CSV format. Let's select all projects again,
resubmit the report and download the CSV file::

    >>> browser.getControl(name='form.project_or_client').value = ('all',)
    >>> browser.getControl('Submit').click()
    >>> browser.getLink('Download CSV').click()
    >>> csv = ('User,Project,Task,Description,Date,Hours\r\n'
    ...        'user,Project One,A simple task,Write document,%s,6\r\n'
    ...        'user,Project One,A simple task,Close this task,%s,3\r\n'
    ...        'user,Project Two,Define requirements,Meeting with Joe,%s,4\r\n'
    ...        ) % (yesterday, today, today)
    >>> browser.contents == csv
    True

Another report is the `Tasks report`, which queries the tasks worked by a user
(or all of them) in a range of dates. The results are presented ordered by
project and by task, showing the total amount of hours used for each task and
listing the users that logged some time in that task. A sum of hours worked in
the project during the period being queried is also displayed.

Let's go the the `Tasks report` page::

    >>> browser.open('http://localhost/app')
    >>> browser.getLink('Reports').click()
    >>> browser.getLink('Tasks report').click()
    >>> 'Run tasks report' in browser.contents
    True

The `from` and `to` dates are set to today::

    >>> browser.getControl(name='form.from_date').value == today
    True
    >>> browser.getControl(name='form.to_date').value == today
    True

All users and all projects are selected by default::

    >>> browser.getControl(name='form.projects').value
    ['all']
    >>> browser.getControl(name='form.user').value
    ['all']

So, if we run the report with those options, we should get only today's tasks,
which in this case are both tasks we created::

    >>> browser.getControl('Submit').click()
    >>> 'A simple task' in browser.contents
    True
    >>> 'Define requirements' in browser.contents
    True

And if we restrict the report to `Project Two`, only `Define requirements` will
be in the results::

    >>> browser.getControl(name='form.projects').value = \
    ...     ('/app/projects/project-two',)
    >>> browser.getControl('Submit').click()
    >>> 'A simple task' in browser.contents
    False
    >>> 'Define requirements' in browser.contents
    True

