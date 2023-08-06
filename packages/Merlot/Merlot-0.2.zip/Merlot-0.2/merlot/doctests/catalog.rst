Catalog
-------

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer


We create a project::

    >>> from datetime import datetime
    >>> from merlot.project import Project
    >>> project = Project()
    >>> project.title = u'Testing'
    >>> project.start_date = datetime(2010, 10, 10).date()
    >>> project.id = 'test'
    >>> app['test'] = project

We make a catalog query to find the project we've just added::

    >>> from zope.component import getUtility
    >>> from zope.catalog.interfaces import ICatalog
    >>> catalog = getUtility(ICatalog, context=app)
    >>> result = catalog.searchResults(title='Testing')
    >>> len(result)
    1
    >>> list(result)[0].title
    u'Testing'
    >>> list(result)[0].start_date
    datetime.date(2010, 10, 10)

Let's test the `project` and `task` indexes. To do so, let's create a task a
log inside that task::

    >>> from merlot.project import Task, Log
    >>> task = Task()
    >>> task.title = 'A sample task'
    >>> task.description = ''
    >>> task.id = 'a-sample-task'
    >>> app['test'][task.id] = task
    >>> log = Log()
    >>> log.description = 'Bla, bla'
    >>> app['test'][task.id]['1'] = log

Let's see what's in the `project` and `task` indexes for the log we've just
created according to the catalog::

    >>> result = catalog.searchResults(description='bla')
    >>> len(result)
    1
    >>> logi = list(result)[0]
    >>> logi.description
    'Bla, bla'

Well, let's see what's the intid associated with our project and task::

    >>> from zope.intid.interfaces import IIntIds
    >>> intids = getUtility(IIntIds, name='intids', context=app)
    >>> project_id = intids.getId(app['test'])
    >>> task_id = intids.getId(app['test']['a-sample-task'])

And finally we can compare the actual intids with the values indexed by the
catalog::

    >>> project_id == logi.project()
    True
    >>> task_id == logi.task()
    True

