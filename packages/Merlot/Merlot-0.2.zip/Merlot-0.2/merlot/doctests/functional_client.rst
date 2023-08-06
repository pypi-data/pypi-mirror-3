Client Model Functional Tests
-----------------------------

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

Now we create a new user that we will use through this document::

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

Let's create a `client`. First we click to `Clients` tab::

    >>> browser.getLink('Clients').click()
    >>> 'There are currently no clients.' in browser.contents
    True

And we add a client::

    >>> browser.getLink('Add new Client').click()
    >>> browser.getControl(name='form.title').value = u'Acme'
    >>> browser.getControl(name='form.type').value = ('NGO',)
    >>> browser.getControl("Add client").click()
    >>> 'Client added' in browser.contents
    True
    >>> 'There are currently no clients.' in browser.contents
    False

We edit the client we've just created::

    >>> browser.getLink('edit').click()
    >>> browser.url
    'http://localhost/app/clients/1/edit'
    >>> browser.getControl(name='form.title').value = u'Some Company'
    >>> browser.getControl(name='form.type').value = ('Company',)
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Let's now create a new project associated with the client we created::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('Add new Project').click()
    >>> browser.getControl(name="form.title").value = u'Project'
    >>> browser.getControl(name='form.client').value = ('/app/clients/1',)
    >>> browser.getControl('Add project').click()
    >>> 'Project added' in browser.contents
    True

If we try to delete the client, we will not be able to because it has a client
associated::

    >>> browser.getLink('Clients').click()
    >>> browser.getLink('delete').click()
    >>> 'Are you sure you want to delete the "Some Company" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'This client cannot be deleted because it has projects associated' in \
    ...     browser.contents
    True

So, let's delete the project and try again::

    >>> browser.getLink('Projects').click()
    >>> browser.getLink('delete').click()
    >>> 'Are you sure you want to delete the "Project" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Project deleted' in browser.contents
    True

Now we go back and try to delete the client::

    >>> browser.getLink('Clients').click()
    >>> browser.getLink('delete').click()
    >>> 'Are you sure you want to delete the "Some Company" item?' in \
    ...     browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Client deleted' in browser.contents
    True
