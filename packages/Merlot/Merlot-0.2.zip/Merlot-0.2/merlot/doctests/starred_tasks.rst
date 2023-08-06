Starred Tasks
-------------

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer

Starred tasks are tasks that the user selects to appear allways on top on his
or her dashboard. They are implemented as annotations on the user account
model. That is, the objects that store the users information (the model
implements merlot.interfaces.IAccount). The annotations are managed via an
adapter.

We need to create an account object::

    >>> from merlot.auth import Account
    >>> user_account = Account('testuser', 'secret', u'Test User')

Now we can adapt the account object and manipulate a list of integer values
which are intended to be tasks integer IDs that you can get by using the
integer IDs local utility::

    >>> from merlot.interfaces import IStarredTasks
    >>> starred_tasks = IStarredTasks(user_account)
    >>> starred_tasks.getStarredTasks()
    []
    >>> starred_tasks.addStarredTask(23)
    >>> starred_tasks.addStarredTask(44523)
    >>> starred_tasks.getStarredTasks()
    [23, 44523]

And we can delete items::

    >>> starred_tasks.removeStarredTask(44523)
    >>> starred_tasks.getStarredTasks()
    [23]

If we try to delete an item that doesn't exist, nothing happens::

    >>> starred_tasks.removeStarredTask(344)
    >>> starred_tasks.getStarredTasks()
    [23]
