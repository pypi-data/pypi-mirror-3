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
"""Table-based program command dispatcher.

This dispatcher supports a 'named command' dispatch similar to that
found in the standard CVS and Subversion client applications.

$Id: command.py 72418 2007-02-07 11:48:58Z oestermeier $
"""
import getopt
import os.path
import sys


from zope.fssync.fsutil import Error


class Usage(Error):
    """Subclass for usage error (command-line syntax).

    You should return an exit status of 2 rather than 1 when catching this.
    """


class Command(object):

    def __init__(self, name=None, usage=None):
        if name is None:
            name = os.path.basename(sys.argv[0])
        self.program = name
        if usage is None:
            import __main__
            usage = __main__.__doc__
        self.helptext = usage
        self.command_table = {}
        self.global_options = []
        self.local_options = []
        self.command = None

    def addCommand(self, name, function, short="", long="", aliases=""):
        names = [name] + aliases.split()
        cmdinfo = short, long.split(), function
        for n in names:
            assert n not in self.command_table
            self.command_table[n] = cmdinfo

    def main(self, args=None):
        try:
            self.realize()
            self.run()

        except Usage, msg:
            self.usage(sys.stderr, msg)
            self.usage(sys.stderr, 'for help use "%(program)s help"')
            return 2

        except Error, msg:
            self.usage(sys.stderr, msg)
            return 1

        except SystemExit:
            raise

        else:
            return None

    def realize(self, args=None):
        if "help" not in self.command_table:
            self.addCommand("help", self.help)
        short, long, func = self.command_table["help"]
        for alias in ("h", "?"):
            if alias not in self.command_table:
                self.addCommand(alias, func, short, " ".join(long))
        if args is None:
            args = sys.argv[1:]
        self.global_options, args = self.getopt("global",
                                                args, "h", ["help"],
                                                self.helptext)
        if not args:
            raise Usage("missing command argument")
        self.command = args.pop(0)
        if self.command not in self.command_table:
            raise Usage("unrecognized command")
        cmdinfo = self.command_table[self.command]
        short, long, func = cmdinfo
        short = "h" + short
        long = ["help"] + list(long)
        self.local_options, self.args = self.getopt(self.command,
                                                    args, short, long,
                                                    func.__doc__)

    def getopt(self, cmd, args, short, long, helptext):
        try:
            opts, args = getopt.getopt(args, short, long)
        except getopt.error, e:
            raise Usage("%s option error: %s", cmd, e)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage(sys.stdout, helptext)
                sys.exit()
        return opts, args

    def run(self):
        _, _, func = self.command_table[self.command]
        func(self.local_options, self.args)

    def usage(self, file, text):
        text = str(text)
        try:
            text = text % {"program": self.program}
        except:
            pass
        print >>file, text

    def help(self, opts, args):
        """%(program)s help [COMMAND ...]

        Display help text.  If COMMAND is specified, help text about
        each named command is displayed, otherwise general help about
        using %(program)s is shown.
        """
        if not args:
            self.usage(sys.stdout, self.helptext)
        else:
            for cmd in args:
                if cmd not in self.command_table:
                    print >>sys.stderr, "unknown command:", cmd
            first = True
            for cmd in args:
                cmdinfo = self.command_table.get(cmd)
                if cmdinfo is None:
                    continue
                _, _, func = cmdinfo
                if first:
                    first = False
                else:
                    print
                self.usage(sys.stdout, func.__doc__)
