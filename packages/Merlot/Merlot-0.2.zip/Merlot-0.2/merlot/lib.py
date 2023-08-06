"""Helpers and other stuff"""

import os.path
from StringIO import StringIO
import csv

from zope.component import getUtility
from grokcore.view import PageTemplateFile

from plone.i18n.normalizer.interfaces import IIDNormalizer

# Constants
PACKAGE_HOME = os.path.join(os.path.dirname(__file__))
DATE_FORMAT = '%Y-%m-%d'

# Template files used application wide
default_form_template = PageTemplateFile(os.path.join('app_templates',
                                                      'form.pt'))
master_template = PageTemplateFile(os.path.join('app_templates', 'master.pt'))


def normalize(title):
    """Normalize a string to make it suitable for an URL"""
    util = getUtility(IIDNormalizer)
    return util.normalize(title)


class CSVGenerator(object):
    """A CSV file generator"""

    def __init__(self, rows, keys):
        self.rows = rows
        self.titles = keys

    def _encode_row(self, row):
        sane_row = []
        for value in row:
            value = unicode(value)
            sane_value = value.encode('utf-8')
            sane_row.append(sane_value)
        return sane_row

    def generate(self):
        """Generate the CSV file"""
        f = StringIO()
        csv_writer = csv.writer(f)
        titles = map(lambda x: x.capitalize(), self.titles)
        titles = self._encode_row(titles)
        csv_writer.writerow(titles)

        for item in self.rows:
            l = []
            for k in self.titles:
                l.append(item[k])
            row = self._encode_row(l)
            csv_writer.writerow(row)

        return f
