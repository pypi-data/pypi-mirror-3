#! /usr/bin/env python
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
"""Filesystem synchronization utility for Zope 3.

Command line syntax summary:

%(program)s add [options] PATH ...
%(program)s checkin [options] URL [TARGETDIR]
%(program)s checkout [options] URL [TARGETDIR]
%(program)s commit [options] [TARGET ...]
%(program)s copy [options] SOURCE [TARGET]
%(program)s diff [options] [TARGET ...]
%(program)s login [options] URL
%(program)s logout [options] URL
%(program)s mkdir PATH ...
%(program)s remove [options] TARGET ...
%(program)s resolve PATH ...
%(program)s revert PATH ...
%(program)s status [options] [TARGET ...]
%(program)s update [TARGET ...]

``%(program)s help'' prints the global help (this message)
``%(program)s help command'' prints the local help for the command
"""
"""
$Id: main.py 73012 2007-03-06 17:16:44Z oestermeier $
"""

import os
import urlparse

from zope.app.fssync.command import Command, Usage
from zope.app.fssync.fssync import FSSync
from zope.fssync import fsutil

def main():
    """Main program.

    The return value is the suggested sys.exit() status code:
    0 or None for success
    2 for command line syntax errors
    1 or other for later errors
    """
    cmd = Command(usage=__doc__)
    for func, aliases, short, long in command_table:
        cmd.addCommand(func.__name__, func, short, long, aliases)

    return cmd.main()

def checkout(opts, args):
    """%(program)s checkout [-u user] URL [TARGETDIR]

    URL should be of the form ``http://user:password@host:port/path''.
    Only http and https are supported (and https only where Python has
    been built to support SSL).  This should identify a Zope 3 server;
    user:password should have management privileges; /path should be
    the traversal path to an existing object, not including views or
    skins.  The user may be specified using the -u option instead of
    encoding it in the URL, since the URL syntax for username and
    password isn't so well known.  The password may be omitted; if so,
    an authentication token stored using '%(program)s login' will be
    used if available; otherwise you will be propted for the password.

    TARGETDIR should be a directory; if it doesn't exist, it will be
    created.  The object tree rooted at /path is copied to a
    subdirectory of TARGETDIR whose name is the last component of
    /path.  TARGETDIR defaults to the current directory.  A metadata
    directory named @@Zope is also created in TARGETDIR.
    """
    if not args:
        raise Usage("checkout requires a URL argument")
    rooturl = args[0]
    if len(args) > 1:
        target = args[1]
        if len(args) > 2:
            raise Usage("checkout requires at most one TARGETDIR argument")
    else:
        target = os.curdir
    user = _getuseroption(opts)
    if user:
        parts = list(urlparse.urlsplit(rooturl))
        netloc = parts[1]
        if "@" in netloc:
            user_passwd, host_port = netloc.split("@", 1)
            if ":" in user_passwd:
                u, p = user_passwd.split(":", 1)
            else:
                u = user_passwd
            # only scream if the -u option and the URL disagree:
            if u != user:
                raise Usage("-u/--user option and URL disagree on user name")
        else:
            # no username in URL; insert
            parts[1] = "%s@%s" % (user, netloc)
        rooturl = urlparse.urlunsplit(tuple(parts))
    fs = FSSync(rooturl=rooturl)
    fs.checkout(target)

def commit(opts, args):
    """%(program)s commit [-m message] [-r] [TARGET ...]

    Commit the TARGET files or directories to the Zope 3 server
    identified by the checkout command.  TARGET defaults to the
    current directory.  Each TARGET is committed separately.  Each
    TARGET should be up-to-date with respect to the state of the Zope
    3 server; if not, a detailed error message will be printed, and
    you should use the update command to bring your working directory
    in sync with the server.

    The -m option specifies a message to label the transaction.
    The default message is 'fssync_commit'.
    """
    message, opts = extract_message(opts, "commit")
    raise_on_conflicts = False
    for o, a in opts:
        if o in ("-r", "--raise-on-conflicts"):
            raise_on_conflicts = True
    fs = FSSync(overwrite_local=True)
    fs.multiple(args, fs.commit, message, raise_on_conflicts)

def update(opts, args):
    """%(program)s update [TARGET ...]

    Bring the TARGET files or directories in sync with the
    corresponding objects on the Zope 3 server identified by the
    checkout command.  TARGET defaults to the current directory.  Each
    TARGET is updated independently.  This command will merge your
    changes with changes made on the server; merge conflicts will be
    indicated by diff3 markings in the file and noted by a 'C' in the
    update output.
    """
    fs = FSSync()
    fs.multiple(args, fs.update)

def add(opts, args):
    """%(program)s add [-t TYPE] [-f FACTORY] TARGET ...

    Add the TARGET files or directories to the set of registered
    objects.  Each TARGET must exist.  The next commit will add them
    to the Zope 3 server.

    The options -t and -f can be used to set the type and factory of
    the newly created object; these should be dotted names of Python
    objects.  Usually only the factory needs to be specified.

    If no factory is specified, the type will be guessed when the
    object is inserted into the Zope 3 server based on the filename
    extension and the contents of the data.  For example, some common
    image types are recognized by their contents, and the extensions
    .pt and .dtml are used to create page templates and DTML
    templates, respectively.
    """
    type = None
    factory = None
    for o, a in opts:
        if o in ("-t", "--type"):
            type = a
        elif o in ("-f", "--factory"):
            factory = a
    if not args:
        raise Usage("add requires at least one TARGET argument")
    fs = FSSync()
    for a in args:
        fs.add(a, type, factory)

def copy(opts, args):
    """%(program)s copy [-l | -R] SOURCE [TARGET]

    """
    recursive = None
    for o, a in opts:
        if o in ("-l", "--local"):
            if recursive:
                raise Usage("%r conflicts with %r" % (o, recursive))
            recursive = False
        elif o in ("-R", "--recursive"):
            if recursive is False:
                raise Usage("%r conflicts with -l" % o)
            recursive = o
    if not args:
        raise Usage("copy requires at least one argument")
    if len(args) > 2:
        raise Usage("copy allows at most two arguments")
    source = args[0]
    if len(args) == 2:
        target = args[1]
    else:
        target = None
    if recursive is None:
        recursive = True
    else:
        recursive = bool(recursive)
    fs = FSSync()
    fs.copy(source, target, children=recursive)

def remove(opts, args):
    """%(program)s remove TARGET ...

    Remove the TARGET files or directories from the set of registered
    objects.  No TARGET must exist.  The next commit will remove them
    from the Zope 3 server.
    """
    if not args:
        raise Usage("remove requires at least one TARGET argument")
    fs = FSSync()
    for a in args:
        fs.remove(a)

diffflags = ["-b", "-B", "--brief", "-c", "-C", "--context",
             "-i", "-u", "-U", "--unified"]
def diff(opts, args):
    """%(program)s diff [diff_options] [TARGET ...]

    Write a diff listing for the TARGET files or directories to
    standard output.  This shows the differences between the working
    version and the version seen on the server by the last update.
    Nothing is printed for files that are unchanged from that version.
    For directories, a recursive diff is used.

    Various GNU diff options can be used, in particular -c, -C NUMBER,
    -u, -U NUMBER, -b, -B, --brief, and -i.
    """
    diffopts = []
    mode = 1
    need_original = True
    for o, a in opts:
        if o == '-1':
            mode = 1
        elif o == '-2':
            mode = 2
        elif o == '-3':
            mode = 3
        elif o == '-N':
            need_original = False
        elif o in diffflags:
            if a:
                diffopts.append(o + " " + a)
            else:
                diffopts.append(o)
    diffopts = " ".join(diffopts)
    fs = FSSync()
    fs.multiple(args, fs.diff, mode, diffopts, need_original)

def status(opts, args):
    """%(program)s status [-v] [--verbose] [TARGET ...]

    Print brief (local) status for each target, without changing any
    files or contacting the Zope server.

    If the -v or --verbose switches are provided, prints a complete
    list of local files regardless of their status.
    """
    verbose = False
    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True
    fs = FSSync()
    fs.multiple(args, fs.status, False, verbose)

def checkin(opts, args):
    """%(program)s checkin [-m message] URL [TARGETDIR]

    URL should be of the form ``http://user:password@host:port/path''.
    Only http and https are supported (and https only where Python has
    been built to support SSL).  This should identify a Zope 3 server;
    user:password should have management privileges; /path should be
    the traversal path to a non-existing object, not including views
    or skins.

    TARGETDIR should be a directory; it defaults to the current
    directory.  The object tree rooted at TARGETDIR is copied to
    /path.  subdirectory of TARGETDIR whose name is the last component
    of /path.
    """
    message, opts = extract_message(opts, "checkin")
    if not args:
        raise Usage("checkin requires a URL argument")
    rooturl = args[0]
    if len(args) > 1:
        target = args[1]
        if len(args) > 2:
            raise Usage("checkin requires at most one TARGETDIR argument")
    else:
        target = os.curdir
    fs = FSSync(rooturl=rooturl, overwrite_local=True)
    fs.checkin(target, message)

def login(opts, args):
    """%(program)s login [-u user] [URL]

    Save a basic authentication token for a URL that doesn't include a
    password component.
    """
    _loginout(opts, args, "login", FSSync().login)

def logout(opts, args):
    """%(program)s logout [-u user] [URL]

    Remove a saved basic authentication token for a URL.
    """
    _loginout(opts, args, "logout", FSSync().logout)

def _loginout(opts, args, cmdname, cmdfunc):
    url = user = None
    if args:
        if len(args) > 1:
            raise Usage("%s allows at most one argument" % cmdname)
        url = args[0]
    user = _getuseroption(opts)
    cmdfunc(url, user)

def _getuseroption(opts):
    user = None
    for o, a in opts:
        if o in ("-u", "--user"):
            if user:
                raise Usage("-u/--user may only be specified once")
            user = a
    return user

def mkdir(opts, args):
    """%(program)s mkdir PATH ...

    Create new directories in directories that are already known to
    %(program)s and schedule the new directories for addition.
    """
    fs = FSSync()
    fs.multiple(args, fs.mkdir)

def resolve(opts, args):
    """%(program)s resolve [PATH ...]

    Clear any conflict markers associated with PATH.  This would allow
    commits to proceed for the relevant files.
    """
    fs = FSSync()
    fs.multiple(args, fs.resolve)

def revert(opts, args):
    """%(program)s revert [TARGET ...]

    Revert changes to targets.  Modified files are overwritten by the
    unmodified copy cached in @@Zope/Original/ and scheduled additions
    and deletions are de-scheduled.  Additions that are de-scheduled
    do not cause the working copy of the file to be removed.
    """
    fs = FSSync()
    fs.multiple(args, fs.revert)

def merge(opts, args):
    """%(program)s merge [TARGETDIR] SOURCEDIR

    Merge changes from one sandbox directory to another. If two
    directories are specified then the first one is the target and the
    second is the source. If only one directory is specified, then the
    target directory is assumed to the be current sandbox.
    """
    if len(args) not in (1,2):
        raise Usage('Merge requires one or two arguments')
    fs = FSSync()
    fs.merge(args)

def extract_message(opts, cmd):
    L = []
    message = None
    msgfile = None
    for o, a in opts:
        if o in ("-m", "--message"):
            if message:
                raise Usage(cmd + " accepts at most one -m/--message option")
            message = a
        elif o in ("-F", "--file"):
            if msgfile:
                raise Usage(cmd + " accepts at most one -F/--file option")
            msgfile = a
        else:
            L.append((o, a))
    if not message:
        if msgfile:
            message = open(msgfile).read()
        else:
            message = "fssync_" + cmd
    elif msgfile:
        raise Usage(cmd + " requires at most one of -F/--file or -m/--message")
    return message, L

command_table = [
    # name is taken from the function name
    # function, aliases,  short opts,   long opts
    (add,      "",        "f:t:",       "factory= type="),
    (checkin,  "",        "F:m:",       "file= message="),
    (checkout, "co",      "u:",         "user="),
    (commit,   "ci",      "F:m:r",      "file= message= raise-on-conflicts"),
    (copy,     "cp",      "lR",         "local recursive"),
    (diff,     "di",      "bBcC:iNuU:", "brief context= unified="),
    (login,    "",        "u:",         "user="),
    (logout,   "",        "u:",         "user="),
    (merge,    "",        "",           ""),
    (mkdir,    "",        "",           ""),
    (remove,   "del delete rm", "",     ""),
    (resolve,  "resolved","",           ""),
    (revert,   "",        "",           ""),
    (status,   "stat st", "v",          "verbose"),
    (update,   "up",      "",           ""),
    ]
