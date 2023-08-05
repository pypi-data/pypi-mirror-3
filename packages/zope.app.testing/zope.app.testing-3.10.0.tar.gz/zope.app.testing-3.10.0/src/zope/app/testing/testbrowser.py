import sys

from zope.app.testing.functional import HTTPCaller

import zope.testbrowser.connection

class PublisherConnection(object):
    """A ``mechanize`` compatible connection object."""

    def __init__(self, host, timeout=None):
        self.caller = HTTPCaller()
        self.host = host

    def set_debuglevel(self, level):
        pass

    def _quote(self, url):
        # the publisher expects to be able to split on whitespace, so we have
        # to make sure there is none in the URL
        return url.replace(' ', '%20')

    def request(self, method, url, body=None, headers=None):
        """Send a request to the publisher.

        The response will be stored in ``self.response``.
        """
        if body is None:
            body = ''

        if url == '':
            url = '/'

        url = self._quote(url)
        # Extract the handle_error option header
        if sys.version_info >= (2,5):
            handle_errors_key = 'X-Zope-Handle-Errors'
        else:
            handle_errors_key = 'X-zope-handle-errors'
        handle_errors_header = headers.get(handle_errors_key, True)
        if handle_errors_key in headers:
            del headers[handle_errors_key]
        # Translate string to boolean.
        handle_errors = {'False': False}.get(handle_errors_header, True)

        # Construct the headers.
        header_chunks = []
        if headers is not None:
            for header in headers.items():
                header_chunks.append('%s: %s' % header)
            headers = '\n'.join(header_chunks) + '\n'
        else:
            headers = ''

        # Construct the full HTTP request string, since that is what the
        # ``HTTPCaller`` wants.
        request_string = (method + ' ' + url + ' HTTP/1.1\n'
                          + headers + '\n' + body)
        self.response = self.caller(request_string, handle_errors)

    def getresponse(self):
        """Return a ``mechanize`` compatible response.

        The goal of ths method is to convert the Zope Publisher's reseponse to
        a ``mechanize`` compatible response, which is also understood by
        mechanize.
        """
        real_response = self.response._response
        status = real_response.getStatus()
        reason = real_response._reason # XXX add a getReason method

        headers = real_response.getHeaders()
        headers.sort()
        headers.insert(0, ('Status', real_response.getStatusString()))
        headers = '\r\n'.join('%s: %s' % h for h in headers)
        content = real_response.consumeBody()
        return zope.testbrowser.connection.Response(content, headers, status, reason)


class PublisherHTTPHandler(zope.testbrowser.connection.HTTPHandler):
    """Special HTTP handler to use the Zope Publisher."""

    def _connect(self, *args, **kw):
        return PublisherConnection(*args, **kw)


class PublisherMechanizeBrowser(zope.testbrowser.connection.MechanizeBrowser):
    """Special ``mechanize`` browser using the Zope Publisher HTTP handler."""

    def _http_handler(self, *args, **kw):
        return PublisherHTTPHandler(*args, **kw)


class Browser(zope.testbrowser.browser.Browser):
    """A Zope `testbrowser` Browser that uses the Zope Publisher."""

    def __init__(self, url=None):
        mech_browser = PublisherMechanizeBrowser()
        super(Browser, self).__init__(url=url, mech_browser=mech_browser)

