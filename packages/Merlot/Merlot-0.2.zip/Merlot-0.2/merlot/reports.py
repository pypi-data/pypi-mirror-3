"""Reports"""

from collections import  defaultdict
import grok
from datetime import datetime
from zope.interface import Interface
from zope.component import getMultiAdapter, getUtility
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from z3c.objpath.interfaces import IObjectPath

from merlot import interfaces as ifaces
from merlot.lib import master_template, default_form_template, CSVGenerator, \
    DATE_FORMAT
from merlot import MerlotMessageFactory as _


def build_logs_report_query(data):
    intids = getUtility(IIntIds, name='intids')
    obpath = getUtility(IObjectPath)

    query = {
        'content_type': ('Log', 'Log'),
        'date': (data['from_date'], data['to_date']),
    }

    project_path = data['project_or_client']
    if project_path != 'all':
        query['project'] = 2 * (intids.getId(obpath.resolve(project_path)),)

    user_id = data['user']
    if user_id != 'all':
        query['user'] = 2 * (data['user'],)

    return query


class ReportsIndex(grok.View):
    grok.context(ifaces.IMerlot)
    grok.name('reports')
    grok.require('merlot.Manage')
    template = master_template


class ReportsIndexViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(ifaces.IMerlot)
    grok.template('reports_index')
    grok.view(ReportsIndex)
    grok.order(10)


class LogsReportForm(grok.Form):
    grok.context(ifaces.IMerlot)
    grok.name('logs-report-form')
    form_fields = grok.AutoFields(ifaces.ILogsReport)
    label = _(u'Run logs report')
    template = default_form_template

    # This will be used in the template to apply the 'compact-form'
    # class to the form tag. This will basically display the fields
    # inline instead of one below the other.
    compact = True

    @grok.action(_(u'Submit'))
    def submit(self, **data):
        catalog = getUtility(ICatalog, context=grok.getSite())
        query = build_logs_report_query(data)

        self.logs = list(catalog.searchResults(**query))
        self.logs.sort(key=lambda x: x.date)
        self.total_hours = sum([l.hours for l in self.logs])
        self.csv_url = ('@@logs-report-csv?project_or_client=%s&'
                        'from_date=%s&to_date=%s&user=%s') % \
                        (data['project_or_client'],
                         data['from_date'],
                         data['to_date'],
                         data['user'])

    def setUpWidgets(self, ignore_request=False):
        super(LogsReportForm, self).setUpWidgets(ignore_request)
        self.widgets['from_date']._data = datetime.now().strftime(DATE_FORMAT)
        self.widgets['to_date']._data = datetime.now().strftime(DATE_FORMAT)

        # Prepopulate the form with values from the request
        for key, value in self.request.form.items():
            name = key.split('.')[-1]
            if self.widgets.get(name):
                self.widgets[name].setRenderedValue(value)


class LogsReport(grok.View):
    grok.context(ifaces.IMerlot)
    grok.name('logs-report')
    grok.require('merlot.Manage')
    template = master_template


class LogsReportViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(LogsReport)
    grok.template('logsreport_viewlet')
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='logs-report-form')
        self.form.update_form()


class CSVLogsReport(grok.View):
    grok.context(ifaces.IMerlot)
    grok.name('logs-report-csv')
    grok.require('merlot.Manage')

    def render(self):
        catalog = getUtility(ICatalog, context=grok.getSite())
        request = self.request
        to_date = lambda x: datetime.strptime(x, DATE_FORMAT).date()

        data = {}
        data['from_date'] = to_date(request['from_date'])
        data['to_date'] = to_date(request['to_date'])
        data['project_or_client'] = request['project_or_client']
        data['user'] = request['user']

        query = build_logs_report_query(data)

        logs = list(catalog.searchResults(**query))
        logs.sort(key=lambda x: x.date)

        log_dicts = []

        for log in logs:
            d = {'user': log.user,
                 'project': log.__parent__.__parent__.title,
                 'task': log.__parent__.title,
                 'description': log.description,
                 'date': log.date,
                 'hours': log.hours}
            log_dicts.append(d)

        keys = ('user', 'project', 'task', 'description', 'date', 'hours')
        csv = CSVGenerator(log_dicts, keys).generate()
        self.response.setHeader('Content-Disposition',
                                'attachment; filename=report.csv;')
        csv.seek(0)
        return csv.read()


### Tasks reports ###
class TasksReportForm(grok.Form):
    grok.context(ifaces.IMerlot)
    grok.name('tasks-report-form')
    form_fields = grok.AutoFields(ifaces.ITasksReport)
    label = _('Run tasks report')
    template = default_form_template

    # This will be used in the template to apply the 'compact-form'
    # class to the form tag. This will basically display the fields
    # inline instead of one below the other.
    compact = True

    def _query(self, data):
        """build the query to the catalog
        """
        intids = getUtility(IIntIds, name='intids')
        obpath = getUtility(IObjectPath)

        query = {
            'content_type': ('Log', 'Log'),
            'date': (data['from_date'], data['to_date']),
        }

        project_path = data['projects']
        if project_path != 'all':
            projects = (intids.getId(obpath.resolve(project_path)),)
            query['project'] = 2 * projects

        user_id = data['user']
        if user_id != 'all':
            query['user'] = 2 * (user_id,)

        return query

    def _results(self, data):
        """Make the query and transform the result in a dict with the
        necessary data to display in the.
        """
        catalog = getUtility(ICatalog, context=grok.getSite())
        intids = getUtility(IIntIds, name='intids')

        results = defaultdict(lambda: {'hours': 0,
                                       'tasks': defaultdict(\
                                                lambda: {'users': set(),
                                                         'hours': 0})})

        query = self._query(data)
        logs = list(catalog.searchResults(**query))
        for log in logs:
            task = intids.getObject(log.task())
            project = intids.getObject(log.project())
            # projects data
            results[log.project()]['id'] = project.id
            results[log.project()]['title'] = project.title
            results[log.project()]['url'] = self.url(project)
            results[log.project()]['hours'] += log.hours
            # task data
            results[log.project()]['tasks'][log.task()]['id'] = task.id
            results[log.project()]['tasks'][log.task()]['title'] = task.title
            results[log.project()]['tasks'][log.task()]['url'] = self.url(task)
            results[log.project()]['tasks'][log.task()]['hours'] += log.hours
            results[log.project()]['tasks'][log.task()]['users'].add(log.user)

        return results

    @grok.action(_('Submit'))
    def submit(self, **data):
        self.results = self._results(data)
        #FIXME: this should by done in the _result method
        self.total_hours = sum([res['hours'] for res in self.results.values()])
        self.csv_url = ('@@tasks-report-csv?projects=%s&'
                        'from_date=%s&to_date=%s&user=%s') % \
                        (data['projects'],
                         data['from_date'],
                         data['to_date'],
                         data['user'])

    def setUpWidgets(self, ignore_request=False):
        super(TasksReportForm, self).setUpWidgets(ignore_request)
        self.widgets['from_date']._data = datetime.now().strftime(DATE_FORMAT)
        self.widgets['to_date']._data = datetime.now().strftime(DATE_FORMAT)

        # Prepopulate the form with values from the request
        for key, value in self.request.form.items():
            name = key.split('.')[-1]
            if self.widgets.get(name):
                self.widgets[name].setRenderedValue(value)


class TasksReport(grok.View):
    grok.context(ifaces.IMerlot)
    grok.name('tasks-report')
    grok.require('merlot.Manage')
    template = master_template


class TasksReportViewlet(grok.Viewlet):
    grok.viewletmanager(ifaces.IMain)
    grok.context(Interface)
    grok.view(TasksReport)
    grok.template('tasksreport_viewlet')
    grok.order(10)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='tasks-report-form')
        self.form.update_form()
