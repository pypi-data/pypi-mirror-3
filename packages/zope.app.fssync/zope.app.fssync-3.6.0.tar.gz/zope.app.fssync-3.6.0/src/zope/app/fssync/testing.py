##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""zope.app.fssync common test related classes/functions/objects.

$Id: testing.py 72426 2007-02-07 13:57:45Z baijum $
"""

__docformat__ = "reStructuredText"

import os
from cStringIO import StringIO
from zope.app.testing.functional import ZCMLLayer
from zope.testbrowser.testing import PublisherConnection
from zope.app.fssync import fssync
from zope.fssync import fsutil


AppFSSyncLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'AppFSSyncLayer', allow_teardown=True)


class TestNetwork(fssync.Network):
    """A specialization which uses a PublisherConnection suitable 
    for functional doctests.
    """

    def __init__(self, handle_errors=True):
        super(TestNetwork, self).__init__()
        self.handle_errors = handle_errors

    def httpreq(self, path, view, datasource=None,
                content_type="application/x-snarf",
                expected_type="application/x-snarf",
                ):
        """Issue an request.
        
        This is a overwritten version of the original Network.httpreq
        method that uses a TestConnection as a replacement for httplib 
        connections.
        """
        assert self.rooturl
        if not path.endswith("/"):
            path += "/"
        path += view
        conn = PublisherConnection(self.host_port)
        headers = {}
        if datasource is None:
            method = 'GET'
        else:
            method = 'POST'
            headers["Content-type"] = content_type
            stream = StringIO()
            datasource(stream)
            headers["Content-Length"] = str(stream.tell())
            
        if self.user_passwd:
            if ":" not in self.user_passwd:
                auth = self.getToken(self.roottype,
                                     self.host_port,
                                     self.user_passwd)
            else:
                auth = self.createToken(self.user_passwd)
            headers['Authorization'] = 'Basic %s' % auth
        headers['Host'] = self.host_port
        headers['Connection'] = 'close'
        headers['X-zope-handle-errors'] = self.handle_errors

        data = None
        if datasource is not None:
            data = stream.getvalue()

        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()

        if response.status != 200:
            raise fsutil.Error("HTTP error %s (%s); error document:\n%s",
                        response.status, response.reason,
                        self.slurptext(response.content_as_file, response.msg))
        elif expected_type and response.msg["Content-type"] != expected_type:
            raise fsutil.Error(
                        self.slurptext(response.content_as_file, response.msg))
        else:
            return response.content_as_file, response.msg

