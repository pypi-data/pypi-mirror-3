##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""XMLRPC testing helpers for Zope 3.

$Id: xmlrpc.py 116141 2010-09-02 15:05:04Z patricks $
"""

import httplib
import StringIO
import xmlrpclib

from zope.app.testing.functional import HTTPCaller


class FakeSocket(object):

    def __init__(self, data):
        self.data = data

    def makefile(self, mode, bufsize=None):
        return StringIO.StringIO(self.data)


class ZopeTestTransport(xmlrpclib.Transport):
    """xmlrpclib transport that delegates to
    zope.app.testing.functional.HTTPCaller.

    It can be used like a normal transport, including support for basic
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: text/xml\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        request += "\n" + request_body
        response = HTTPCaller()(request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )
        res = httplib.HTTPResponse(FakeSocket(response.getBody()))
        res.begin()
        return self.parse_response(res)


def ServerProxy(uri, transport=None, encoding=None,
                verbose=0, allow_none=0, handleErrors=True):
    """A factory that creates a server proxy using the ZopeTestTransport
    by default.

    """
    if transport is None:
        transport = ZopeTestTransport()
    if isinstance(transport, ZopeTestTransport):
        transport.handleErrors = handleErrors
    return xmlrpclib.ServerProxy(uri, transport, encoding, verbose, allow_none)
