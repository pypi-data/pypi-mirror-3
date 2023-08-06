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
"""Test the authentication token manager.

$Id: test_passwd.py 26559 2004-07-15 21:22:32Z srichter $
"""
import os
import tempfile
import unittest

from zope.app.fssync import passwd


class PasswordGetter(object):
    """PasswordManager.getPassword() replacement to use in the tests."""

    def __call__(self, user, host_port):
        self.user = user
        self.host_port = host_port
        return "mypassword"


class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.filename = tempfile.mktemp()
        self.pwmgr = passwd.PasswordManager(filename=self.filename)
        self.getter = PasswordGetter()
        self.pwmgr.getPassword = self.getter

    def tearDown(self):
        if os.path.exists(self.filename):
            os.unlink(self.filename)

    def create_file(self, include_comment=True):
        """Create the file with a single record."""
        f = open(self.filename, "w")
        if include_comment:
            print >>f, "# this is a comment"
        print >>f
        print >>f, "http", "example.com", "testuser", "faketoken"
        f.close()

    def read_file(self):
        """Return a list of non-blank, non-comment lines from the file."""
        f = open(self.filename)
        lines = f.readlines()
        f.close()
        return [line.split()
                for line in lines
                if line.strip()[:1] not in ("#", "")]

    # getToken()

    def test_hostport_normalization(self):
        token1 = self.pwmgr.getToken("http", "example.com", "testuser")
        token2 = self.pwmgr.getToken("http", "example.com:80", "testuser")
        self.assertEqual(token1, token2)
        self.assertEqual(self.getter.host_port, "example.com")

    def test_load_token_from_file(self):
        self.create_file()
        token = self.pwmgr.getToken("http", "example.com:80", "testuser")
        self.assertEqual(token, "faketoken")
        self.failIf(hasattr(self.getter, "user"))
        self.failIf(hasattr(self.getter, "host_post"))

    def test_load_token_missing_from_file(self):
        self.create_file()
        token = self.pwmgr.getToken("http", "example.com:80", "otheruser")
        self.assertNotEqual(token, "faketoken")
        self.assertEqual(self.getter.user, "otheruser")
        self.assertEqual(self.getter.host_port, "example.com")

    def test_diff_in_scheme(self):
        self.create_file()
        token = self.pwmgr.getToken("https", "example.com", "testuser")
        self.assertNotEqual(token, "faketoken")

    def test_diff_in_host(self):
        self.check_difference("http", "example.net", "testuser")

    def test_diff_in_port(self):
        self.check_difference("http", "example.com:9000", "testuser")

    def test_diff_in_username(self):
        self.check_difference("http", "example.com", "otheruser")

    def check_difference(self, scheme, host_port, username):
        self.create_file()
        token = self.pwmgr.getToken(scheme, host_port, username)
        self.assertNotEqual(token, "faketoken")
        self.assertEqual(self.getter.user, username)
        self.assertEqual(self.getter.host_port, host_port)

    # addToken()

    def test_add_token_to_new_file(self):
        self.pwmgr.addToken("http", "example.com:80", "testuser", "faketoken")
        records = self.read_file()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0],
                         ["http", "example.com", "testuser", "faketoken"])

    def test_add_token_to_file(self):
        self.create_file()
        self.pwmgr.addToken("http", "example.com", "otheruser", "mytoken")
        records = self.read_file()
        records.sort()
        self.assertEqual(len(records), 2)
        self.assertEqual(records,
                         [["http", "example.com", "otheruser", "mytoken"],
                          ["http", "example.com", "testuser",  "faketoken"],
                          ])

    def test_replace_token_from_file(self):
        self.create_file()
        self.pwmgr.addToken("http", "example.com", "testuser", "newtoken")
        records = self.read_file()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0],
                         ["http", "example.com", "testuser", "newtoken"])

    # removeToken()

    def test_remove_without_file(self):
        found = self.pwmgr.removeToken("http", "example.com", "someuser")
        self.assert_(not found)

    def test_remove_not_in_file(self):
        self.create_file()
        found = self.pwmgr.removeToken("http", "example.com", "someuser")
        self.assert_(not found)
        # file should not have been modified
        records = self.read_file()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0],
                         ["http", "example.com", "testuser", "faketoken"])

    def test_remove_last_in_file_with_comment(self):
        self.create_file()
        found = self.pwmgr.removeToken("http", "example.com", "testuser")
        self.assert_(found)
        records = self.read_file()
        self.assertEqual(len(records), 0)
        # the file included a comment, so must not have been removed:
        self.assert_(os.path.exists(self.filename))

    def test_remove_last_in_file_without_comment(self):
        self.create_file(include_comment=False)
        found = self.pwmgr.removeToken("http", "example.com", "testuser")
        self.assert_(found)
        # the result should only include a blank line, so should be removed:
        self.assert_(not os.path.exists(self.filename))

    def test_remove_one_of_two(self):
        f = open(self.filename, "w")
        print >>f, "http", "example.com", "testuser",  "faketoken"
        print >>f, "http", "example.com", "otheruser", "othertoken"
        f.close()
        found = self.pwmgr.removeToken("http", "example.com", "testuser")
        self.assert_(found)
        records = self.read_file()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0],
                         ["http", "example.com", "otheruser", "othertoken"])


def test_suite():
    return unittest.makeSuite(TestPasswordManager)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
