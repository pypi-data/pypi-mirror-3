### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
import base64
import cookielib
import urllib2
import xmlrpclib

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


class XMLRPCCookieAuthTransport(xmlrpclib.Transport):
    """An XML-RPC transport handling authentication via cookies"""

    def __init__(self, user_agent, credentials=(), cookies=None):
        xmlrpclib.Transport.__init__(self)
        self.user_agent = user_agent
        self.credentials = credentials
        self.cookies = cookies

    # override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        xmlrpclib.Transport.send_host(self, connection, host)
        if (self.cookies is not None) and (len(self.cookies) > 0):
            for cookie in self.cookies:
                connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))
        elif self.credentials:
            auth = 'Basic %s' % base64.encodestring("%s:%s" % self.credentials).strip()
            connection.putheader('Authorization', auth)

    def request(self, host, handler, request_body, verbose=False):

        # dummy request class for extracting cookies
        class CookieRequest(urllib2.Request):
            pass

        # dummy response class for extracting cookies
        class CookieResponse:
            def __init__(self, headers):
                self.headers = headers
            def info(self):
                return self.headers

        # issue XML-RPC request
        connection = self.make_connection(host)
        self.verbose = verbose
        if verbose:
            connection.set_debuglevel(1)
        self.send_request(connection, handler, request_body)
        self.send_host(connection, host)
        self.send_user_agent(connection)
        # get response
        self.send_content(connection, request_body)
        errcode, errmsg, headers = connection.getreply()
        # extract cookies from response headers
        crequest = CookieRequest('http://%s/' % host)
        cresponse = CookieResponse(headers)
        if self.cookies is not None:
            self.cookies.extract_cookies(cresponse, crequest)
        if errcode != 200:
            raise xmlrpclib.ProtocolError(host + handler, errcode, errmsg, headers)
        try:
            sock = connection._conn.sock
        except AttributeError:
            sock = None
        return self._parse_response(connection.getfile(), sock)


def getClient(uri, credentials=(), verbose=False):
    """Get an XML-RPC client which supports basic authentication"""
    transport = XMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY basic implementation)', credentials)
    return xmlrpclib.Server(uri, transport=transport, verbose=verbose)


def getClientWithCookies(uri, credentials=(), verbose=False):
    """Get an XML-RPC client which supports authentication throught cookies"""
    transport = XMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY cookie implementation)', credentials, cookielib.CookieJar())
    return xmlrpclib.Server(uri, transport=transport, verbose=verbose)
