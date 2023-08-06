import z3c.testsetup
from zope.app.wsgi.testlayer import BrowserLayer
from zope.app.component.hooks import setSite
from zope.fanstatic.testing import ZopeFanstaticBrowserLayer

import merlot
from merlot.app import Merlot

browser_layer = ZopeFanstaticBrowserLayer(merlot)

def setup(test):
    root = browser_layer.getRootFolder()
    root['app'] = Merlot()
    setSite(root['app'])
    test.globs['app'] = root['app']

def teardown(test):
    # Hardest line to find ever
    setSite(None)

test_suite = z3c.testsetup.register_all_tests('merlot')
