Users, Authentication & Authorization Functional Tests
------------------------------------------------------

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer

In Merlot there are only two roles: authenticated and anonymous. If you are
authenticated you have full access to the system; if you are not logged in, you
have no permissions.

We need to create a user to play with later. First of all we access the site
as admin::

    >>> from zope.app.wsgi.testlayer import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic admin:admin')
    >>> browser.open('http://localhost/app')
    >>> 'Logged in as: Manager' in browser.contents
    True

Now we create a new user. To do so, we click on the `Users` tab and then on the
`Add new User` link::

    >>> browser.getLink('Users').click()
    >>> 'There are currently no users.' in browser.contents
    True
    >>> browser.getLink('Add new User').click()

We fill the `add user form`::

    >>> browser.getControl(name="form.id").value = u'user'
    >>> browser.getControl(name="form.real_name").value = u'Testing User'
    >>> browser.getControl(name="form.password").value = u'secret'
    >>> browser.getControl(name="form.confirm_password").value = u'secret'

Submit the form and check that the changes were saved::

    >>> browser.getControl("Add user").click()
    >>> 'User added' in browser.contents
    True
    >>> 'Testing User' in browser.contents
    True

We are now ready to start testing permissions. First of all, let's log out from
the site to test that we can't access any pages::

    >>> browser = Browser()
    >>> browser.open('http://localhost/app')
    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2F%40%40index'

We can't access the projects container::

    >>> browser.open('http://localhost/app/projects')
    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2Fprojects%2F%40%40index'

We can't access the reports either::

    >>> browser.open('http://localhost/app/@@logs-report')
    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2F%40%40logs-report'

    >>> browser.open('http://localhost/app/@@tasks-report')
    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2F%40%40tasks-report'

We can't access the clients container::

    >>> browser.open('http://localhost/app/clients')
    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2Fclients%2F%40%40index'

Now we authenticate using the user we created using the login form::

    >>> browser.open('http://localhost/app')
    >>> browser.getControl(name="form.username").value = u'user'
    >>> browser.getControl(name="form.password").value = u'secret'
    >>> browser.getControl("Login").click()
    >>> 'You are logged in.' in browser.contents
    True

And we can access everything. For example, we can access the projects
container::

    >>> browser.getLink('Projects').click()
    >>> browser.url
    'http://localhost/app/projects'

We can also access the reports::

    >>> browser.open('http://localhost/app/@@logs-report')
    >>> browser.url
    'http://localhost/app/@@logs-report'

    >>> browser.open('http://localhost/app/@@tasks-report')
    >>> browser.url
    'http://localhost/app/@@tasks-report'

We can also access the clients container::

    >>> browser.open('http://localhost/app/clients')
    >>> browser.url
    'http://localhost/app/clients'

Let's go to the `user folder` and create a new user::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('Add new User').click()

If we try too set a user name with strange characters, the form submission will
fail::

    >>> browser.getControl(name="form.id").value = u'jdoe/'
    >>> browser.getControl(name="form.real_name").value = u'John Doe'
    >>> browser.getControl(name="form.password").value = u'easy'
    >>> browser.getControl(name="form.confirm_password").value = u'easy'
    >>> browser.getControl("Add user").click()
    >>> 'Invalid user name, only characters in [a-z0-9] are allowed' in \
    ...     browser.contents
    True

Let's also check that no user were created in the ZODB by checking that the
only existing user is the one we created at the beginning::

    >>> users = app['users']
    >>> len(users.values())
    1
    >>> users.values()[0].id
    'user'

Let's fix the user name in the form and see what happens if we enter different
values in the `password` and `confirm password` fields::

    >>> browser.getControl(name="form.id").value = u'jdoe'
    >>> browser.getControl(name="form.real_name").value = u'John Doe'
    >>> browser.getControl(name="form.password").value = u'something'
    >>> browser.getControl(name="form.confirm_password").value = u'different'
    >>> browser.getControl("Add user").click()
    >>> 'Passwords does not match' in browser.contents
    True

Let's finally fill the form properly and create the user::

    >>> browser.getControl(name="form.password").value = u'something'
    >>> browser.getControl(name="form.confirm_password").value = u'something'
    >>> browser.getControl("Add user").click()
    >>> 'User added' in browser.contents
    True
    >>> 'John Doe' in browser.contents
    True

And the user is now persisted::

    >>> len(users.values())
    2
    >>> 'jdoe' in [u.id for u in users.values()]
    True

We can now edit the user we've just added::

    >>> browser.getLink('edit', index=0).click()
    >>> 'jdoe' in browser.contents
    True

There is a `username` field in the edit form, but its value can't be changed.
We don't allow user IDs to change as they are used to reference users in other
parts of the system::

    >>> try:
    ...     browser.getControl(name='form.id').value = 'changed'
    ... except AttributeError as detail:
    ...     detail
    AttributeError("control 'form.id' is readonly",)
    
Let's change the `real name` to something else and save the changes::

    >>> browser.getControl(name='form.real_name').value = u'Something Else'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

We got redirected to the container user folder::

    >>> browser.url
    'http://localhost/app/users'

And the change is in place::

    >>> 'Something Else' in browser.contents
    True

Let's check that the password for the user `Something Else` was no modified. So
we logout::

    >>> browser = Browser()

And we use the login form to login into the site::

    >>> browser.open('http://localhost/app')
    >>> browser.getControl(name="form.username").value = u'jdoe'
    >>> browser.getControl(name="form.password").value = u'something'
    >>> browser.getControl("Login").click()
    >>> 'You are logged in.' in browser.contents
    True

Let's change the password of the user we first created::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('edit', index=1).click()
    >>> 'Testing User' in browser.contents
    True

Once again, if we enter different values for the `password` and `confirm
password` fields, we get a validation error::

    >>> browser.getControl(name="form.password").value = u'super'
    >>> browser.getControl(name="form.confirm_password").value = u'super2'
    >>> browser.getControl('Save').click()
    >>> 'Passwords does not match' in browser.contents
    True
    >>> browser.url
    'http://localhost/app/users/user/edit'

So, let's change the password for real::

    >>> browser.getControl(name="form.password").value = u'super'
    >>> browser.getControl(name="form.confirm_password").value = u'super'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.url
    'http://localhost/app/users'

Now let's try to change our own password::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('edit', index=0).click()
    >>> 'jdoe' in browser.contents
    True
    >>> browser.getControl(name="form.password").value = u'supersecret'
    >>> browser.getControl(name="form.confirm_password").value = u'supersecret'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

As our credentials changed, we are kicked off the site::

    >>> browser.url
    'http://localhost/app/@@login?camefrom=http%3A%2F%2Flocalhost%2Fapp%2Fusers%2F%40%40index'

The old credentials are no longer valid::

    >>> browser.getControl(name="form.username").value = u'jdoe'
    >>> browser.getControl(name="form.password").value = u'something'
    >>> browser.getControl("Login").click()
    >>> 'Invalid username and/or password' in browser.contents
    True

Let's login back using the new password::

    >>> browser.getControl(name="form.username").value = u'jdoe'
    >>> browser.getControl(name="form.password").value = u'supersecret'
    >>> browser.getControl("Login").click()
    >>> 'You are logged in.' in browser.contents
    True

Now let's delete the user `Testing User`::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('delete', index=1).click()
    >>> 'Are you sure you want to delete the "user" item?' in browser.contents
    True

We can cancel the deletion, in that case, the user won't be deleted and we will
get redirected to the user listing::

    >>> browser.getControl('Cancel').click()
    >>> browser.url
    'http://localhost/app/users'
    >>> 'Testing User' in browser.contents
    True

Well, let's delete the user for real now::

    >>> browser.getLink('Users').click()
    >>> browser.getLink('delete', index=1).click()
    >>> 'Are you sure you want to delete the "user" item?' in browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'User deleted.' in browser.contents
    True

And let's logout from the site::

    >>> browser.getLink('Logout').click()
    >>> browser.url.startswith('http://localhost/app/@@login')
    True
