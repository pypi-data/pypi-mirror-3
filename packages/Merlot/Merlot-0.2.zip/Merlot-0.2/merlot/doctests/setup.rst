Setup
-----

.. :doctest:
.. :setup: merlot.tests.setup
.. :teardown: merlot.tests.teardown
.. :layer: merlot.tests.browser_layer

The `app` variable is binded in out tests setup to a brand new created Merlot
object. The Merlot object has a title::

    >>> app.title
    u'Merlot \u2014 Project Management Software'

When the application is created, containers for projects, clients and users get
also created::

    >>> 'projects' in app
    True
    >>> 'clients' in app
    True
    >>> 'users' in app
    True
    >>> project_container = app['projects']
    >>> client_container = app['clients']
    >>> userfolder = app['users']

Let's check that `projects_container` and `clients_container` are what we
expect them to be::

    >>> project_container.title
    u'Projects'
    >>> client_container.title
    u'Clients'
    >>> from merlot.interfaces import IProjectContainer, IClientContainer
    >>> IProjectContainer.providedBy(project_container)
    True
    >>> IClientContainer.providedBy(client_container)
    True

There are a few local utilities registered in the Merlot application. We have
local utilities to manage users and authentication::

    >>> from zope.component import getUtility
    >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
    >>> from zope.app.security.interfaces import IAuthentication
    >>> users = getUtility(IAuthenticatorPlugin, 'users', context=app)
    >>> auth = getUtility(IAuthentication, context=app)

Also, an integer IDs local utility is registered. This allow us to create an
integer ID for each object and later look up objects by their IDs::

    >>> from zope.intid.interfaces import IIntIds
    >>> intids = getUtility(IIntIds, name='intids', context=app)

The last local utility registered is a relation catalog utility that allow us
to keep track of relations between objects::

    >>> from zc.relation.interfaces import ICatalog
    >>> rel_catalog = getUtility(ICatalog, context=app)

A global utility is registered to resolve to an object given a path and vice
versa::

    >>> from z3c.objpath.interfaces import IObjectPath
    >>> object_path = getUtility(IObjectPath)
    >>> object_path.path(app['projects'])
    u'/app/projects'
    >>> object_path.resolve(u'/app/projects') == app['projects']
    True
