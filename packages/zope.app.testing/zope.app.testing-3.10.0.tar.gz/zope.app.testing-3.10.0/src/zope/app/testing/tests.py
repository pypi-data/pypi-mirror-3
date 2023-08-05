##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test tcpdoc

$Id: tests.py 123984 2012-01-07 17:43:12Z menesis $
"""
from doctest import DocTestSuite
import os
import re
import unittest
import StringIO

from zope.testing.renormalizing import RENormalizing
from zope.component import getAllUtilitiesRegisteredFor
from ZODB.interfaces import IDatabase

import zope.app.testing
from zope.app.publication.requestpublicationregistry import factoryRegistry
from zope.app.publication.requestpublicationfactories import BrowserFactory
from zope.app.testing import functional
from zope.app.testing.dochttp import dochttp
import transaction
from zope.app.testing.functional import SampleFunctionalTest
from zope.app.testing.functional import BrowserTestCase, HTTPTestCase
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.app.testing.functional import FunctionalTestCase
from zope.app.testing.functional import FunctionalTestSetup
from zope.app.testing.testing import AppTestingLayer

from zope.app.testing.testing import FailingKlass


HEADERS = """\
HTTP/1.1 200 OK
Content-Type: text/plain
"""

BODY = """\
This is the response body.
"""

here = os.path.dirname(zope.app.testing.__file__)
directory = os.path.join(here, 'recorded')

expected = r'''

  >>> print http(r"""
  ... GET /@@contents.html HTTP/1.1
  ... """)
  HTTP/1.1 401 Unauthorized
  Content-Length: 89
  Content-Type: text/html;charset=utf-8
  Www-Authenticate: basic realm="Zope"
  <BLANKLINE>
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <BLANKLINE>
  ...
  <BLANKLINE>
  </html>
  <BLANKLINE>
  <BLANKLINE>


  >>> print http(r"""
  ... GET /@@contents.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... """)
  HTTP/1.1 200 OK
  Content-Length: 89
  Content-Type: text/html;charset=utf-8
  <BLANKLINE>
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <BLANKLINE>
  ...
  <BLANKLINE>
  </html>
  <BLANKLINE>
  <BLANKLINE>


  >>> print http(r"""
  ... GET /++etc++site/@@manage HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Referer: http://localhost:8081/
  ... """)
  HTTP/1.1 303 See Other
  Content-Length: 0
  Content-Type: text/plain;charset=utf-8
  Location: @@tasks.html
  <BLANKLINE>


  >>> print http(r"""
  ... GET / HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... """)
  HTTP/1.1 200 OK
  Content-Length: 89
  Content-Type: text/html;charset=utf-8
  <BLANKLINE>
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <BLANKLINE>
  ...
  <BLANKLINE>
  </html>
  <BLANKLINE>
  <BLANKLINE>


  >>> print http(r"""
  ... GET /++etc++site/@@tasks.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Referer: http://localhost:8081/
  ... """)
  HTTP/1.1 200 OK
  Content-Length: 89
  Content-Type: text/html;charset=utf-8
  <BLANKLINE>
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <BLANKLINE>
  ...
  <BLANKLINE>
  </html>
  <BLANKLINE>
  <BLANKLINE>
'''


class FunctionalHTTPDocTest(unittest.TestCase):

    def test_dochttp(self):
        import sys
        old = sys.stdout
        sys.stdout = StringIO.StringIO()
        dochttp(['-p', 'test', directory])
        got = sys.stdout.getvalue()
        sys.stdout = old
        self.assertEquals(expected, got)


class AuthHeaderTestCase(unittest.TestCase):

    def test_auth_encoded(self):
        auth_header = functional.auth_header
        header = 'Basic Z2xvYmFsbWdyOmdsb2JhbG1ncnB3'
        self.assertEquals(auth_header(header), header)

    def test_auth_non_encoded(self):
        auth_header = functional.auth_header
        header = 'Basic globalmgr:globalmgrpw'
        expected = 'Basic Z2xvYmFsbWdyOmdsb2JhbG1ncnB3'
        self.assertEquals(auth_header(header), expected)

    def test_auth_non_encoded_empty(self):
        auth_header = functional.auth_header
        header = 'Basic globalmgr:'
        expected = 'Basic Z2xvYmFsbWdyOg=='
        self.assertEquals(auth_header(header), expected)
        header = 'Basic :pass'
        expected = 'Basic OnBhc3M='
        self.assertEquals(auth_header(header), expected)

    def test_auth_non_encoded_colon(self):
        auth_header = zope.app.testing.functional.auth_header
        header = 'Basic globalmgr:pass:pass'
        expected = 'Basic Z2xvYmFsbWdyOnBhc3M6cGFzcw=='
        self.assertEquals(auth_header(header), expected)


class HTTPCallerTestCase(unittest.TestCase):

    def test_chooseRequestClass(self):
        from zope.publisher.interfaces import IRequest, IPublication

        factoryRegistry.register('GET', '*', 'browser', 0, BrowserFactory())

        caller = functional.HTTPCaller()
        request_class, publication_class = caller.chooseRequestClass(
            method='GET', path='/', environment={})

        self.assert_(IRequest.implementedBy(request_class))
        self.assert_(IPublication.implementedBy(publication_class))


class DummyCookiesResponse(object):
    # Ugh, this simulates the *internals* of a HTTPResponse object
    # TODO: expand the IHTTPResponse interface to give access to all cookies
    _cookies = None

    def __init__(self, cookies=None):
        if not cookies:
            cookies = {}
        self._cookies = cookies


class CookieHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.handler = functional.CookieHandler()

    def test_saveCookies(self):
        response = DummyCookiesResponse(dict(
            spam=dict(value='eggs', path='/foo', comment='rest is ignored'),
            monty=dict(value='python')))
        self.handler.saveCookies(response)
        self.assertEqual(len(self.handler.cookies), 2)
        self.assert_(self.handler.cookies['spam'].OutputString() in
                         ('spam=eggs; Path=/foo;', 'spam=eggs; Path=/foo'))
        self.assert_(self.handler.cookies['monty'].OutputString() in
                         ('monty=python;', 'monty=python'))

    def test_httpCookie(self):
        cookies = self.handler.cookies
        cookies['spam'] = 'eggs'
        cookies['spam']['path'] = '/foo'
        cookies['bar'] = 'baz'
        cookies['bar']['path'] = '/foo/baz'
        cookies['monty'] = 'python'

        cookieHeader = self.handler.httpCookie('/foo/bar')
        parts = cookieHeader.split('; ')
        parts.sort()
        self.assertEqual(parts, ['monty=python', 'spam=eggs'])

        cookieHeader = self.handler.httpCookie('/foo/baz')
        parts = cookieHeader.split('; ')
        parts.sort()
        self.assertEqual(parts, ['bar=baz', 'monty=python', 'spam=eggs'])

    # There is no test for CookieHandler.loadCookies because it that method
    # only passes the arguments on to Cookie.BaseCookie.load, which the
    # standard library has tests for (we hope).


class HTTPFunctionalTest(HTTPTestCase):

    def testNoDefaultReferer(self):
        # There should be no referer set in the request by default.
        r = self.makeRequest()
        self.assertRaises(KeyError, r.environment.__getitem__, 'HTTP_REFERER')


class BrowserFunctionalTest(BrowserTestCase):

    def testNoDefaultReferer(self):
        # There should be no referer set in the request by default.
        r = self.makeRequest()
        self.assertRaises(KeyError, r.environment.__getitem__, 'HTTP_REFERER')


class HTTPCallerFunctionalTest(FunctionalTestCase):

    def testNoDefaultReferer(self):
        # There should be no referer set in the request by default.
        from zope.app.testing.functional import HTTPCaller
        http = HTTPCaller()
        response = http("GET /++skin++Basic HTTP/1.1\n\n")
        self.assertRaises(KeyError, response._request.environment.__getitem__,
                          'HTTP_REFERER')

    def testRemoteAddr(self):
        # There should be a REMOTE_ADDR in the request by default.
        from zope.app.testing.functional import HTTPCaller
        http = HTTPCaller()
        response = http("GET / HTTP/1.1\n\n")
        self.assertEqual(response._request.environment['REMOTE_ADDR'],
                         '127.0.0.1')


class GetCookies(object):
    """Get all cookies set."""

    def __call__(self):
        cookies = ['%s=%s'%(k, v)
                   for k, v in self.request.getCookies().items()]
        cookies.sort()
        return ';'.join(cookies)


class SetCookies(object):
    """Set a specific cookie."""

    def __call__(self):
        self.request.response.setCookie('bid', 'bval')


class Echo(object):
    """Simply echo the interesting parts of the request"""

    def __call__(self):
        items = []
        for k in sorted(self.request.keys()):
            if k in self.request.form:
                continue
            v = self.request.get(k, None)
            items.append('%s: %s' % (k, v))
        items.extend('%s: %s' % x for x in sorted(self.request.form.items())) 
        items.append('Body: %r' % self.request.bodyStream.read())
        return '\n'.join(items)


class EchoOne(object):
    """Echo one variable from the request"""

    def __call__(self):
        return repr(self.request.get(self.request.form['var']))


class CookieFunctionalTest(BrowserTestCase):

    """Functional tests should handle cookies like a web browser

    Multiple requests in the same test should acumulate cookies.
    We also ensure that cookies with path values are only sent for
    the correct URL's so we can test cookies don't 'leak'. Expiry,
    secure and other cookie attributes are not being worried about
    at the moment

    """

    def setUp(self):
        import zope.configuration.xmlconfig

        super(CookieFunctionalTest, self).setUp()
        self.assertEqual(
                len(self.cookies.keys()), 0,
                'cookies store should be empty')

        zope.configuration.xmlconfig.string(r'''
        <configure xmlns="http://namespaces.zope.org/browser">

           <include package="zope.browserpage" file="meta.zcml" />

           <page
              name="getcookies"
              for="*"
              permission="zope.Public"
              class="zope.app.testing.tests.GetCookies" />

           <page
              name="setcookie"
              for="*"
              permission="zope.Public"
              class="zope.app.testing.tests.SetCookies" />

        </configure>
        ''')

    def testDefaultCookies(self):
        # By default no cookies are set
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)
        self.assert_(not response._request._cookies)

    def testSimpleCookies(self):
        self.cookies['aid'] = 'aval'
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response._request._cookies['aid'], 'aval')

    def testCookiePaths(self):
        # We only send cookies if the path is correct
        self.cookies['aid'] = 'aval'
        self.cookies['aid']['Path'] = '/sub/folder'
        self.cookies['bid'] = 'bval'
        response = self.publish('/')

        self.assertEquals(response.getStatus(), 200)
        self.assert_('aid' not in response._request._cookies)
        self.assertEquals(response._request._cookies['bid'], 'bval')

    def testHttpCookieHeader(self):
        # Passing an HTTP_COOKIE header to publish adds cookies
        response = self.publish('/', env={
            'HTTP_COOKIE':
                '$Version=1, aid=aval; $Path=/sub/folder, bid=bval'})
        self.assertEquals(response.getStatus(), 200)
        self.failIf('aid' in response._request._cookies)
        self.assertEquals(response._request._cookies['bid'], 'bval')

    def testStickyCookies(self):
        # Cookies should acumulate during the test
        response = self.publish('/', env={'HTTP_COOKIE': 'aid=aval;'})
        self.assertEquals(response.getStatus(), 200)

        # Cookies are implicity passed to further requests in this test
        response = self.publish('/getcookies')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response.getBody().strip(), 'aid=aval')

        # And cookies set in responses also acumulate
        response = self.publish('/setcookie')
        self.assertEquals(response.getStatus(), 200)
        response = self.publish('/getcookies')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response.getBody().strip(), 'aid=aval;bid=bval')


class SkinsAndHTTPCaller(FunctionalTestCase):

    def test_skins(self):
        # Regression test for http://zope.org/Collectors/Zope3-dev/353
        from zope.app.testing.functional import HTTPCaller
        http = HTTPCaller()
        response = http("GET /++skin++Basic HTTP/1.1\n\n")
        self.assert_("zopetopBasic.css" in str(response))


class RetryProblemFunctional(FunctionalTestCase):

    def setUp(self):
        super(RetryProblemFunctional, self).setUp()

        root = self.getRootFolder()

        root['fail'] = FailingKlass()

        transaction.commit()

    def tearDown(self):
        root = self.getRootFolder()
        del root['fail']
        super(RetryProblemFunctional, self).tearDown()

    def test_retryOnConflictErrorFunctional(self):
        from zope.app.testing.functional import HTTPCaller

        http = HTTPCaller()
        response = http(r"""
GET /@@test-conflict-raise-view.html HTTP/1.1
Authorization: Basic mgr:mgrpw
""")

        self.assertNotEqual(response.getStatus(), 599)
        self.assertEqual(response.getStatus(), 500)


class RetryProblemBrowser(BrowserTestCase):
    def setUp(self):
        super(RetryProblemBrowser, self).setUp()

        root = self.getRootFolder()

        root['fail'] = FailingKlass()

        transaction.commit()

    def tearDown(self):
        root = self.getRootFolder()
        del root['fail']
        super(RetryProblemBrowser, self).tearDown()

    def test_retryOnConflictErrorBrowser(self):
        response = self.publish('/@@test-conflict-raise-view.html',
                                handle_errors=True)
        self.assertNotEqual(response.getStatus(), 599)
        self.assertEqual(response.getStatus(), 500)


ftesting_zcml = os.path.join(here, 'ftesting.zcml')


def doctest_FunctionalTestSetup_clears_global_utilities():
    """Test that FunctionalTestSetup doesn't leave global utilities.

    Leaving global IDatabase utilities makes a nice juicy memory leak.
    See https://bugs.launchpad.net/zope3/+bug/251273

    This bug has now been fixed and this test exercises the fixed version.

        >>> setup = FunctionalTestSetup(ftesting_zcml)

    At this point, there are registrations for the base databases created by
    the initialization:

        >>> base, = getAllUtilitiesRegisteredFor(IDatabase)

    Setting up for a test causes overriding registrations to be made:

        >>> setup.setUp()
        >>> dbs = list(getAllUtilitiesRegisteredFor(IDatabase))
        >>> len(dbs)
        1
        >>> base in dbs
        False
        >>> override, = dbs

    Tearing down the test context causes the overriding database to be
    removed:

        >>> setup.tearDown()
        >>> list(getAllUtilitiesRegisteredFor(IDatabase))
        []

    Tearing down completely:

        >>> setup.tearDownCompletely()
    """


empty_zcml = os.path.join(here, 'empty.zcml')


def doctest_FunctionalTestSetup_supports_product_config():
    """Test that FunctionalTestSetup configures products.

    We want to apply the following product configuration before opening
    databases:

        >>> product_config = '''
        ... <product-config abc>
        ...  key1 value1
        ...  key2 value2
        ... </product-config>
        ... '''

    Since we expect the product configuration to be available when the layer
    is initialized, we'll register a subscriber for the IDatabaseOpenedEvent
    event, The normal CA-provided handling of the event is of no use to use,
    since the functional layer controls the configuration of that, but a
    low-level zoe.event subscriber will do the job:

        >>> import zope.event

        >>> def handle_database_open(event):
        ...     global config
        ...     IDbOE = zope.processlifetime.IDatabaseOpened
        ...     if IDbOE.providedBy(event):
        ...         config = zope.app.appsetup.product.getProductConfiguration(
        ...             'abc')

        >>> zope.event.subscribers.append(handle_database_open)

    The product configuration is passed to the layer setup and installed by
    the setUp method:

        >>> import pprint
        >>> import zope.app.appsetup.product

        >>> setup = FunctionalTestSetup(
        ...     empty_zcml, product_config=product_config)

    The configuration was visible to our database-opened subscriber:

        >>> pprint.pprint(config, width=1)
        {'key1': 'value1',
         'key2': 'value2'}

        >>> config = zope.app.appsetup.product.getProductConfiguration(
        ...     'abc')
        >>> pprint.pprint(config, width=1)
        {'key1': 'value1',
         'key2': 'value2'}

    Let's run a test that mutates the product configuration:

        >>> setup.setUp()
        >>> zope.app.appsetup.product.setProductConfiguration(
        ...     'abc', {'another': 'value'})
        >>> zope.app.appsetup.product.getProductConfiguration('abc')
        {'another': 'value'}
        >>> setup.tearDown()

    A second test run in the layer sees the original product configuration:

        >>> setup.setUp()
        >>> config = zope.app.appsetup.product.getProductConfiguration(
        ...     'abc')
        >>> pprint.pprint(config, width=1)
        {'key1': 'value1',
         'key2': 'value2'}
        >>> setup.tearDown()

    After the layer is cleaned up, there's no longer any product
    configuration:

        >>> zope.event.subscribers.remove(handle_database_open)
        >>> setup.tearDownCompletely()

        >>> zope.app.appsetup.product.saveConfiguration()
        {}

    """


def doctest_ZCMLLayer_carries_product_configuration():
    """Show that ``ZCMLLayer`` carries along product configuration.

    ZCML layers can carry be defined to work with specific product
    configuration; this is useful when application code (early subscribers,
    including generations) need configuration data.

    Let's define a couple of separate ZCML layers, and show that the
    configuration data is properly associated with each, and applied at
    appropriate times.

    We'll need two distinct product configurations:

        >>> product_config_one = '''
        ... <product-config abc>
        ...  key1 a1
        ...  key2 a2
        ... </product-config>
        ... '''

        >>> product_config_two = '''
        ... <product-config abc>
        ...  key1 b1
        ...  key2 b2
        ... </product-config>
        ... '''

    We can create two distinct layers that use these configurations:

        >>> LayerOne = functional.ZCMLLayer(
        ...     empty_zcml, 'zope.app.testing.tests', 'LayerOne',
        ...     product_config=product_config_one,
        ...     allow_teardown=True)

        >>> LayerTwo = functional.ZCMLLayer(
        ...     empty_zcml, 'zope.app.testing.tests', 'LayerTwo',
        ...     product_config=product_config_two,
        ...     allow_teardown=True)

    For each layer, we can see that the correct product configuration is
    installed, and subsequent layer usages won't have problems because of the
    previously installed layer.  This checks that initialization and
    deconstruction of the functional test setup is handled properly to allow
    layers to be used in sequence.

    Let's use a helper function to show the configuration:

        >>> import pprint

        >>> def show_config():
        ...     c = zope.app.appsetup.product.getProductConfiguration('abc')
        ...     pprint.pprint(c, width=1)

        >>> LayerOne.setUp()
        >>> show_config()
        {'key1': 'a1',
         'key2': 'a2'}

        >>> LayerOne.tearDown()

        >>> LayerTwo.setUp()
        >>> show_config()
        {'key1': 'b1',
         'key2': 'b2'}

        >>> LayerTwo.tearDown()

    """

def testbrowserSetUp(test):
    import zope.configuration.xmlconfig

    zope.configuration.xmlconfig.string(r'''
    <configure xmlns="http://namespaces.zope.org/browser">

       <include package="zope.browserpage" file="meta.zcml" />

       <page
          name="echo"
          for="*"
          permission="zope.Public"
          class="zope.app.testing.tests.Echo" />

       <page
          name="echo_one"
          for="*"
          permission="zope.Public"
          class="zope.app.testing.tests.EchoOne" />

    </configure>
    ''')


def test_suite():
    checker = RENormalizing([
        (re.compile(r'^HTTP/1.1 (\d{3}) .*?\n'), 'HTTP/1.1 \\1\n')])
    SampleFunctionalTest.layer = AppTestingLayer
    CookieFunctionalTest.layer = AppTestingLayer
    SkinsAndHTTPCaller.layer = AppTestingLayer
    RetryProblemFunctional.layer = AppTestingLayer
    RetryProblemBrowser.layer = AppTestingLayer
    HTTPFunctionalTest.layer = AppTestingLayer
    BrowserFunctionalTest.layer = AppTestingLayer
    HTTPCallerFunctionalTest.layer = AppTestingLayer

    testbrowser_checker = RENormalizing([
        (re.compile(r'Status: 200.*'), 'Status: 200 OK'),
        (re.compile(r'HTTP_USER_AGENT:\s+\S+'),
         'HTTP_USER_AGENT: Python-urllib/2.4'),
        (re.compile(r'Content-[Ll]ength:.*'), 'Content-Length: 123'),
        ])
    testbrowser_test = FunctionalDocFileSuite('testbrowser.txt',
                                              setUp=testbrowserSetUp,
                                              checker=testbrowser_checker)
    testbrowser_test.layer = AppTestingLayer

    doc_test = FunctionalDocFileSuite('doctest.txt', 'cookieTestOne.txt',
        'cookieTestTwo.txt', checker=checker)
    doc_test.layer = AppTestingLayer

    return unittest.TestSuite((
        unittest.makeSuite(FunctionalHTTPDocTest),
        unittest.makeSuite(AuthHeaderTestCase),
        unittest.makeSuite(HTTPCallerTestCase),
        unittest.makeSuite(CookieHandlerTestCase),
        DocTestSuite(),
        unittest.makeSuite(SampleFunctionalTest),
        unittest.makeSuite(HTTPFunctionalTest),
        unittest.makeSuite(BrowserFunctionalTest),
        unittest.makeSuite(HTTPCallerFunctionalTest),
        unittest.makeSuite(CookieFunctionalTest),
        unittest.makeSuite(SkinsAndHTTPCaller),
        unittest.makeSuite(RetryProblemFunctional),
        unittest.makeSuite(RetryProblemBrowser),
        doc_test,
        testbrowser_test,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
