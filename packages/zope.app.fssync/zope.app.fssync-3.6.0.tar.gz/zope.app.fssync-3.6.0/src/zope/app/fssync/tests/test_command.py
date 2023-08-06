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
"""Tests for yet another command-line handler.

$Id: test_command.py 25177 2004-06-02 13:17:31Z jim $
"""

import sys
import unittest

from cStringIO import StringIO

from zope.app.fssync import command


class CommandTests(unittest.TestCase):

    def setUp(self):
        self.called = False
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.new_stdout = StringIO()
        self.new_stderr = StringIO()
        sys.stdout = self.new_stdout
        sys.stderr = self.new_stderr
        self.cmd = command.Command("testcmd", "%(program)s msg")

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def test_no_command(self):
        self.assertRaises(command.Usage, self.cmd.realize, [])

    def test_unknown_command(self):
        self.assertRaises(command.Usage, self.cmd.realize, ["throb"])

    def test_global_help_short(self):
        self.assertRaises(SystemExit, self.cmd.realize, ["-h"])
        self.assert_(self.new_stdout.getvalue())

    def test_global_help_long(self):
        self.assertRaises(SystemExit, self.cmd.realize, ["--help"])
        self.assert_(self.new_stdout.getvalue())

    def test_calling_command(self):
        self.cmd.addCommand("throb", self.mycmd)
        self.cmd.realize(["throb"])
        self.cmd.run()
        self.assertEqual(self.opts, [])
        self.assertEqual(self.args, [])

    def mycmd(self, opts, args):
        """dummy help text"""
        self.called = True
        self.opts = opts
        self.args = args

    def test_calling_command_via_alias(self):
        self.cmd.addCommand("throb", self.mycmd, "x:y", "prev next",
                            aliases="chunk thunk")
        self.cmd.realize(["thunk", "-yx", "42", "--", "-more", "args"])
        self.cmd.run()
        self.assertEqual(self.opts, [("-y", ""), ("-x", "42")])
        self.assertEqual(self.args, ["-more", "args"])

    def test_calling_command_with_args(self):
        self.cmd.addCommand("throb", self.mycmd, "x:", "spew")
        self.cmd.realize(["throb", "-x", "42", "--spew", "more", "args"])
        self.cmd.run()
        self.assertEqual(self.opts, [("-x", "42"), ("--spew", "")])
        self.assertEqual(self.args, ["more", "args"])

    def test_local_help_short(self):
        self.cmd.addCommand("throb", self.mycmd)
        self.assertRaises(SystemExit, self.cmd.realize, ["throb", "-h"])
        self.assert_(self.new_stdout.getvalue())
        self.assert_(not self.called)

    def test_local_help_long(self):
        self.cmd.addCommand("throb", self.mycmd)
        self.assertRaises(SystemExit, self.cmd.realize, ["throb", "--help"])
        self.assert_(self.new_stdout.getvalue())
        self.assert_(not self.called)


def test_suite():
    return unittest.makeSuite(CommandTests)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
