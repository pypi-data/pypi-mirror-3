##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for the Network class.

$Id: test_network.py 26878 2004-08-03 16:25:34Z jim $
"""

import os
import select
import socket
import unittest
import threading

from StringIO import StringIO

from os.path import join

from zope.app.fssync.fssync import Network, Error
from zope.fssync.tests.tempfiles import TempFiles

sample_rooturl = "http://user:passwd@host:8080/path"

HOST = "127.0.0.1"     # localhost
PORT = 60841           # random number
RESPONSE = """HTTP/1.0 404 Not found\r
Content-type: text/plain\r
Content-length: 0\r
\r
"""

class DummyServer(threading.Thread):
    """A server that can handle one HTTP request (returning a 404 error)."""

    def __init__(self, ready):
        self.ready = ready     # Event signaling we're listening
        self.stopping = False
        threading.Thread.__init__(self)

    def run(self):
        svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        svr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        svr.bind((HOST, PORT))
        svr.listen(1)
        self.ready.set()
        conn = None
        sent_response = False
        while not self.stopping:
            if conn is None:
                r = [svr]
            else:
                r = [conn]
            r, w, x = select.select(r, [], [], 0.01)
            if not r:
                continue
            s = r[0]
            if s is svr:
                conn, addr = svr.accept()
                ##print "connect from", `addr`
            else:
                if s is not conn:
                    raise AssertionError("s is not conn")
                data = conn.recv(1000)
                ##print "received", `data`
                if not data:
                    break
                if not sent_response:
                    conn.send(RESPONSE)
                    conn.close()
                    conn = None
                    sent_response = True
        if conn is not None:
            conn.close()
        svr.close()
        ##print "stopped"
        
    def stop(self):
        ##print "stopping"
        self.stopping = True

class TestNetwork(TempFiles):

    def setUp(self):
        TempFiles.setUp(self)
        self.network = Network()

    def test_initial_state(self):
        self.assertEqual(self.network.rooturl, None)
        self.assertEqual(self.network.roottype, None)
        self.assertEqual(self.network.rootpath, None)
        self.assertEqual(self.network.user_passwd, None)
        self.assertEqual(self.network.host_port, None)

    def test_setrooturl(self):
        self.network.setrooturl(sample_rooturl)
        self.assertEqual(self.network.rooturl, sample_rooturl)
        self.assertEqual(self.network.roottype, "http")
        self.assertEqual(self.network.rootpath, "/path")
        self.assertEqual(self.network.user_passwd, "user:passwd")
        self.assertEqual(self.network.host_port, "host:8080")

    def test_setrooturl_nopath(self):
        rooturl = "http://user:passwd@host:8080"
        self.network.setrooturl(rooturl)
        self.assertEqual(self.network.rooturl, rooturl)
        self.assertEqual(self.network.roottype, "http")
        self.assertEqual(self.network.rootpath, "/")
        self.assertEqual(self.network.user_passwd, "user:passwd")
        self.assertEqual(self.network.host_port, "host:8080")

    def test_findrooturl_notfound(self):
        # TODO: This test will fail if a file /tmp/@@Zope/Root exists :-(
        target = self.tempdir()
        self.assertEqual(self.network.findrooturl(target), None)

    def test_findrooturl_found(self):
        target = self.tempdir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        f = open(rootfile, "w")
        f.write(sample_rooturl + "\n")
        f.close()
        self.assertEqual(self.network.findrooturl(target), sample_rooturl)

    def test_saverooturl(self):
        self.network.setrooturl(sample_rooturl)
        target = self.tempdir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        self.network.saverooturl(target)
        f = open(rootfile, "r")
        data = f.read()
        f.close()
        self.assertEqual(data.strip(), sample_rooturl)

    def test_loadrooturl(self):
        target = self.tempdir()
        self.assertRaises(Error, self.network.loadrooturl, target)
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        self.network.setrooturl(sample_rooturl)
        self.network.saverooturl(target)
        new = Network()
        new.loadrooturl(target)
        self.assertEqual(new.rooturl, sample_rooturl)

    def test_httpreq(self):
        ready = threading.Event()
        svr = DummyServer(ready)
        svr.start()
        ready.wait()
        try:
            self.network.setrooturl("http://%s:%s" % (HOST, PORT))
            self.assertRaises(Error, self.network.httpreq, "/xyzzy", "@@view")
        finally:
            svr.stop()
            svr.join()

    def test_slurptext_html(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "text/html"})
        self.assertEqual(result, "This is some text.")

    def test_slurptext_plain(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "text/plain"})
        self.assertEqual(result, "<p>This is some\n\ntext.</p>")

    def test_slurptext_nontext(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "foo/bar"})
        self.assertEqual(result, "Content-type: foo/bar")

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestNetwork)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
