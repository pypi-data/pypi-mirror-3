"""Vocabularies"""

import grok

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from z3c.objpath.interfaces import IObjectPath

from merlot import interfaces as ifaces
from merlot import MerlotMessageFactory as _


class VocabularyFactory(grok.GlobalUtility):
    grok.baseclass()
    grok.implements(ISource, IVocabularyFactory)
    grok.provides(IVocabularyFactory)

    terms = []

    def __call__(self, context=None):
        terms_list = [SimpleTerm(*term) for term in self.terms]
        return SimpleVocabulary(terms_list)


class ProjectVocabulary(grok.GlobalUtility):
    """A vocabulary with all the existing projects"""
    grok.implements(ISource, IVocabularyFactory)
    grok.provides(IVocabularyFactory)
    grok.name('merlot.ProjectVocabulary')

    def __call__(self, context=None):
        site = grok.getSite()
        path = getUtility(IObjectPath).path

        projects = [i for i in site['projects'].values() if \
                    ifaces.IProject.providedBy(i)]
        title = lambda p: '%s (%s)' % (p.title, p.client.to_object.title)

        projects = [SimpleTerm(path(p), path(p), title(p)) for p in projects]

        all_projects = (u'all', u'all', _(u'All projects'))
        projects.insert(0, SimpleTerm(*all_projects))

        return SimpleVocabulary(projects)


class UserVocabulary(grok.GlobalUtility):
    """A vocabulary with all the existing users"""
    grok.implements(ISource, IVocabularyFactory)
    grok.provides(IVocabularyFactory)
    grok.name('merlot.UserVocabulary')

    def __call__(self, context=None):
        site = grok.getSite()
        users = site['users'].values()
        users = [SimpleTerm(u.id, u.id, u.real_name) for u in users]

        all_users = (u'all', u'all', _(u'All users'))
        users.insert(0, SimpleTerm(*all_users))

        return SimpleVocabulary(users)


class TaskPriorityVocabulary(VocabularyFactory):
    """A vocabulary for task priorities"""
    grok.name('merlot.TaskPriorityVocabulary')

    terms = [(u'Critical', u'Critical', _(u'Critical')),
             (u'High', u'High', _(u'High')),
             (u'Normal', u'Normal', _(u'Normal')),
             (u'Low', u'Low', _(u'Low'))]


class ProjectStatusVocabulary(VocabularyFactory):
    """The statuses a project or task can be in"""
    grok.name('merlot.ProjectStatusVocabulary')

    terms = [(u'In progress', u'In progress', _(u'In progress')),
             (u'Blocked', u'Blocked', _(u'Blocked')),
             (u'Completed', u'Completed', _(u'Completed'))]


class ClientTypeVocabulary(VocabularyFactory):
    """The different client types"""
    grok.name('merlot.ClientTypeVocabulary')

    terms = [(u'Company', u'Company', _(u'Company')),
             (u'Government', u'Government', _(u'Government')),
             (u'NGO', u'NGO', _(u'NGO')),
             (u'Internal', u'Internal', _(u'Internal')),
             (u'Individual', u'Individual', _(u'Individual'))]
