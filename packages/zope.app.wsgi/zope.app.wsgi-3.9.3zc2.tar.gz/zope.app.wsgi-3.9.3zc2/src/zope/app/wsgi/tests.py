##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""WSGI tests

$Id: tests.py 124082 2012-01-18 22:49:50Z jim $
"""
import tempfile
import unittest
import re
import zope.component

from zope import component, interface
from zope.component.testlayer import ZCMLFileLayer
from zope.testing import doctest
from zope.testing import renormalizing

import zope.event
import zope.app.wsgi
import zope.publisher.interfaces.browser
from zope.app.publication.requestpublicationregistry import factoryRegistry
from zope.app.publication.requestpublicationfactories import BrowserFactory
from zope.app.wsgi.testing import AppWSGILayer
from zope.authentication.interfaces import IAuthentication
from zope.securitypolicy.tests import principalRegistry


def cleanEvents(s):
    zope.event.subscribers.pop()


class FileView:

    interface.implements(zope.publisher.interfaces.browser.IBrowserPublisher)
    component.adapts(interface.Interface,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, _, request):
        self.request = request

    def browserDefault(self, *_):
        return self, ()

    def __call__(self):
        self.request.response.setHeader('content-type', 'text/plain')
        f = tempfile.TemporaryFile()
        f.write("Hello\nWorld!\n")
        return f


def test_file_returns():
    """We want to make sure that file returns work

Let's register a view that returns a temporary file and make sure that
nothing bad happens. :)

    >>> component.provideAdapter(FileView, name='test-file-view.html')
    >>> from zope.security import checker
    >>> checker.defineChecker(
    ...     FileView,
    ...     checker.NamesChecker(['browserDefault', '__call__']),
    ...     )

    >>> from zope.app.wsgi.testlayer import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.open('http://localhost/@@test-file-view.html')
    >>> browser.headers['content-type']
    'text/plain'

    >>> browser.headers['content-length']
    '13'

    >>> print browser.contents
    Hello
    World!
    <BLANKLINE>

Clean up:

    >>> checker.undefineChecker(FileView)
    >>> component.provideAdapter(
    ...     None,
    ...     (interface.Interface,
    ...      zope.publisher.interfaces.browser.IBrowserRequest),
    ...     zope.publisher.interfaces.browser.IBrowserPublisher,
    ...     'test-file-view.html',
    ...     )

"""

def creating_app_w_paste_emits_ProcessStarting_event():
    """
    >>> import zope.event
    >>> events = []
    >>> subscriber = events.append
    >>> zope.event.subscribers.append(subscriber)

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()
    >>> sitezcml = os.path.join(temp_dir, 'site.zcml')
    >>> open(sitezcml, 'w').write('<configure />')
    >>> zopeconf = os.path.join(temp_dir, 'zope.conf')
    >>> open(zopeconf, 'w').write('''
    ... site-definition %s
    ...
    ... <zodb>
    ...   <mappingstorage />
    ... </zodb>
    ...
    ... <eventlog>
    ...   <logfile>
    ...     path STDOUT
    ...   </logfile>
    ... </eventlog>
    ... ''' % sitezcml)

    >>> import zope.app.wsgi.paste, zope.processlifetime
    >>> app = zope.app.wsgi.paste.ZopeApplication(
    ...     {}, zopeconf, handle_errors=False)

    >>> len([e for e in events
    ...     if isinstance(e, zope.processlifetime.ProcessStarting)]) == 1
    True

    >>> zope.event.subscribers.remove(subscriber)
    """

def test_suite():

    checker = renormalizing.RENormalizing([
        (re.compile(
            r"&lt;class 'zope.component.interfaces.ComponentLookupError'&gt;"),
         r'ComponentLookupError'),
        ])
    functional_suite = doctest.DocTestSuite()
    functional_suite.layer = AppWSGILayer

    readme_test = doctest.DocFileSuite(
            'README.txt',
            checker=checker, tearDown=cleanEvents,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)

    doctest_suite = doctest.DocFileSuite(
            'fileresult.txt', 'paste.txt',
            checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)

    readme_test.layer = ZCMLFileLayer(zope.app.wsgi)
    doctest_suite.layer = ZCMLFileLayer(zope.app.wsgi)


    return unittest.TestSuite((
        functional_suite, readme_test, doctest_suite))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
