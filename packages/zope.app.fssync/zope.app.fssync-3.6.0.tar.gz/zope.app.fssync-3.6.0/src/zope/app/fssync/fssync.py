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
"""Highest-level classes to support filesystem synchronization:

class Network -- handle network connection
class FSSync  -- implement various commands (checkout, commit etc.)

$Id: fssync.py 73012 2007-03-06 17:16:44Z oestermeier $
"""

import os
import sys
import shutil
import urllib
import filecmp
import htmllib
import httplib
import tempfile
import urlparse
import formatter

from StringIO import StringIO

import os.path
from os.path import exists, isfile, isdir
from os.path import dirname, basename, split, join
from os.path import realpath, normcase, normpath

from zope.fssync.metadata import Metadata, dump_entries
from zope.fssync.fsmerger import FSMerger
from zope.fssync.fsutil import Error
from zope.fssync import fsutil
from zope.fssync.snarf import Snarfer, Unsnarfer
from zope.app.fssync.passwd import PasswordManager
from zope.app.fssync.ssh import SSHConnection
import zope.app.fssync.merge

if sys.platform[:3].lower() == "win":
    DEV_NULL = r".\nul"
else:
    DEV_NULL = "/dev/null"


class Network(PasswordManager):

    """Handle network communication.

    This class has various methods for managing the root url (which is
    stored in a file @@Zope/Root) and has a method to send an HTTP(S)
    request to the root URL, expecting a snarf file back (that's all the
    application needs).

    Public instance variables:

    rooturl     -- full root url, e.g. 'http://user:passwd@host:port/path'
    roottype    -- 'http' or 'https'
    user_passwd -- 'user:passwd'
    host_port   -- 'host:port'
    rootpath    -- '/path'
    """

    def __init__(self, rooturl=None):
        """Constructor.  Optionally pass the root url."""
        super(Network, self).__init__()
        self.setrooturl(rooturl)

    def loadrooturl(self, target):
        """Load the root url for the given target.

        This calls findrooturl() to find the root url for the target,
        and then calls setrooturl() to set it.  If self.findrooturl()
        can't find a root url, Error() is raised.
        """
        rooturl = self.findrooturl(target)
        if not rooturl:
            raise Error("can't find root url for target", target)
        self.setrooturl(rooturl)

    def saverooturl(self, target):
        """Save the root url in the target's @@Zope directory.

        This writes the file <target>/@@Zope/Root; the directory
        <target>/@@Zope must already exist.
        """
        if self.rooturl:
            dir = join(target, "@@Zope")
            if not exists(dir):
                os.mkdir(dir)
            fn = join(dir, "Root")
            self.writefile(self.rooturl + "\n",
                           fn)

    def findrooturl(self, target):
        """Find the root url for the given target.

        This looks in <target>/@@Zope/Root, and then in the
        corresponding place for target's parent, and then further
        ancestors, until the filesystem root is reached.

        If no root url is found, return None.
        """
        dir = realpath(target)
        while dir:
            rootfile = join(dir, "@@Zope", "Root")
            try:
                data = self.readfile(rootfile)
            except IOError:
                pass
            else:
                data = data.strip()
                if data:
                    return data
            head, tail = split(dir)
            if tail in fsutil.unwanted:
                break
            dir = head
        return None

    def setrooturl(self, rooturl):
        """Set the root url.

        If the argument is None or empty, self.rooturl and all derived
        instance variables are set to None.  Otherwise, self.rooturl
        is set to the argument the broken-down root url is stored in
        the other instance variables.
        """
        if not rooturl:
            rooturl = roottype = rootpath = user_passwd = host_port = None
        else:
            roottype, rest = urllib.splittype(rooturl)
            if roottype not in ("http", "https", "zsync+ssh"):
                raise Error("root url must be 'http', 'https', or 'zsync+ssh'",
                            rooturl)
            if roottype == "https" and not hasattr(httplib, "HTTPS"):
                raise Error("https not supported by this Python build")
            netloc, rootpath = urllib.splithost(rest)
            if not rootpath:
                rootpath = "/"
            user_passwd, host_port = urllib.splituser(netloc)

        self.rooturl = rooturl
        self.roottype = roottype
        self.rootpath = rootpath
        self.user_passwd = user_passwd
        self.host_port = host_port

    def readfile(self, file, mode="r"):
        # Internal helper to read a file
        f = open(file, mode)
        try:
            return f.read()
        finally:
            f.close()

    def writefile(self, data, file, mode="w"):
        # Internal helper to write a file
        f = open(file, mode)
        try:
            f.write(data)
        finally:
            f.close()

    def httpreq(self, path, view, datasource=None,
                content_type="application/x-snarf",
                expected_type="application/x-snarf"):
        """Issue an HTTP or HTTPS request.

        The request parameters are taken from the root url, except
        that the requested path is constructed by concatenating the
        path and view arguments.

        If the optional 'datasource' argument is not None, it should
        be a callable with a stream argument which, when called,
        writes data to the stream.  In this case, a POST request is
        issued, and the content-type header is set to the
        'content_type' argument, defaulting to 'application/x-snarf'.
        Otherwise (if datasource is None), a GET request is issued and
        no input document is sent.

        If the request succeeds and returns a document whose
        content-type is 'application/x-snarf', the return value is a tuple
        (fp, headers) where fp is a non-seekable stream from which the
        return document can be read, and headers is a case-insensitive
        mapping giving the response headers.

        If the request returns an HTTP error, the Error exception is
        raised.  If it returns success (error code 200) but the
        content-type of the result is not 'application/x-snarf', the Error
        exception is also raised.  In these error cases, if the result
        document's content-type is a text type (anything starting with
        'text/'), the text of the result document is included in the
        Error exception object; in the specific case that the type is
        text/html, HTML formatting is removed using a primitive
        formatter.

        TODO: This doesn't support proxies or redirect responses.
        """
        # TODO: Don't change the case of the header names; httplib might
        # not treat them in a properly case-insensitive manner.
        assert self.rooturl
        if not path.endswith("/"):
            path += "/"
        path = urllib.quote(path)
        path += view
        if self.roottype == "https":
            conn = httplib.HTTPSConnection(self.host_port)
        elif self.roottype == "zsync+ssh":
            conn = SSHConnection(self.host_port, self.user_passwd)
        else:
            conn = httplib.HTTPConnection(self.host_port)

        if datasource is None:
            conn.putrequest("GET", path)
        else:
            conn.putrequest("POST", path)
            conn.putheader("Content-type", content_type)
            #conn.putheader("Transfer-encoding", "chunked")
            #XXX Chunking works only with the zserver. Twisted responds with
            #    HTTP error 400 (Bad Request); error document:
            #      Excess 4 bytes sent in chunk transfer mode
            #We use a buffer as workaround and compute the Content-Length in
            #advance
            tmp = tempfile.TemporaryFile('w+b')
            datasource(tmp)
            conn.putheader("Content-Length", str(tmp.tell()))

        if self.user_passwd:
            if ":" not in self.user_passwd:
                auth = self.getToken(self.roottype,
                                     self.host_port,
                                     self.user_passwd)
            else:
                auth = self.createToken(self.user_passwd)
            conn.putheader('Authorization', 'Basic %s' % auth)
        conn.putheader("Host", self.host_port)
        conn.putheader("Connection", "close")
        conn.endheaders()
        if datasource is not None:
            #XXX If chunking works again, replace the following lines with
            # datasource(PretendStream(conn))
            # conn.send("0\r\n\r\n")
            tmp.seek(0)
            data = tmp.read(1<<16)
            while data:
                conn.send(data)
                data = tmp.read(1<<16)
            tmp.close()

        response = conn.getresponse()
        if response.status != 200:
            raise Error("HTTP error %s (%s); error document:\n%s",
                        response.status, response.reason,
                        self.slurptext(response.fp, response.msg))
        elif expected_type and response.msg["Content-type"] != expected_type:
            raise Error(self.slurptext(response.fp, response.msg))
        else:
            return response.fp, response.msg

    def slurptext(self, fp, headers):
        """Helper to read the result document.

        This removes the formatting from a text/html document; returns
        other text documents as-is; and for non-text documents,
        returns just a string giving the content-type.
        """
        # Too often, we just get HTTP response code 200 (OK), with an
        # HTML document that explains what went wrong.
        data = fp.read()
        ctype = headers.get("Content-type", 'unknown')
        if ctype == "text/html":
            s = StringIO()
            f = formatter.AbstractFormatter(formatter.DumbWriter(s))
            p = htmllib.HTMLParser(f)
            p.feed(data)
            p.close()
            return s.getvalue().strip()
        if ctype.startswith("text/"):
            return data.strip()
        return "Content-type: %s" % ctype

class PretendStream(object):

    """Helper class to turn writes into chunked sends."""

    def __init__(self, conn):
        self.conn = conn

    def write(self, s):
        self.conn.send("%x\r\n" % len(s))
        self.conn.send(s)

class DataSource(object):

    """Helper class to provide a data source for httpreq."""

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __call__(self, f):
        snf = Snarfer(f)
        snf.add(join(self.head, self.tail), self.tail)
        snf.addtree(join(self.head, "@@Zope"), "@@Zope/")

class FSSync(object):

    def __init__(self, metadata=None, network=None, rooturl=None,
                 overwrite_local=False):
        if metadata is None:
            metadata = Metadata()
        if network is None:
            network = Network()
        self.metadata = metadata
        self.network = network
        self.network.setrooturl(rooturl)
        self.fsmerger = FSMerger(self.metadata, self.reporter,
                                 overwrite_local)

    def login(self, url=None, user=None):
        scheme, host_port, user = self.get_login_info(url, user)
        token = self.network.getToken(scheme, host_port, user)
        self.network.addToken(scheme, host_port, user, token)

    def logout(self, url=None, user=None):
        scheme, host_port, user = self.get_login_info(url, user)
        if scheme:
            ok = self.network.removeToken(scheme, host_port, user)
        else:
            # remove both, if present
            ok1 = self.network.removeToken("http", host_port, user)
            ok2 = self.network.removeToken("https", host_port, user)
            ok = ok1 or ok2
        if not ok:
            raise Error("matching login info not found")

    def get_login_info(self, url, user):
        if url:
            parts = urlparse.urlsplit(url)
            scheme = parts[0]
            host_port = parts[1]
            if not (scheme and host_port):
                raise Error(
                    "URLs must include both protocol (http or https)"
                    " and host information")
            if "@" in host_port:
                user_passwd, host_port = host_port.split("@", 1)
                if not user:
                    if ":" in user_passwd:
                        user = user_passwd.split(":", 1)[0]
                    else:
                        user = user_passwd
        else:
            self.network.loadrooturl(os.curdir)
            scheme = self.network.roottype
            host_port = self.network.host_port
            if not user:
                upw = self.network.user_passwd
                if ":" in upw:
                    user = upw.split(":", 1)[0]
                else:
                    user = upw
        if not user:
            user = raw_input("Username: ").strip()
            if not user:
                raise Error("username cannot be empty")
        return scheme, host_port, user

    def checkout(self, target):
        rootpath = self.network.rootpath
        if not rootpath:
            raise Error("root url not set")
        if self.metadata.getentry(target):
            raise Error("target already registered", target)
        if exists(target) and not isdir(target):
            raise Error("target should be a directory", target)
        fsutil.ensuredir(target)
        i = rootpath.rfind("/")
        tail = rootpath[i+1:]
        tail = tail or "root"
        fp, headers = self.network.httpreq(rootpath, "@@toFS.snarf")
        try:
            self.merge_snarffile(fp, target, tail)
        finally:
            fp.close()
        self.network.saverooturl(target)

    def multiple(self, args, method, *more):
        if not args:
            args = [os.curdir]
        for target in args:
            if self.metadata.getentry(target):
                method(target, *more)
            else:
                names = self.metadata.getnames(target)
                if not names:
                    # just raise Error directly?
                    method(target, *more) # Will raise an exception
                else:
                    for name in names:
                        method(join(target, name), *more)

    def commit(self, target, note="fssync_commit", raise_on_conflicts=False):
        entry = self.metadata.getentry(target)
        if not entry:
            raise Error("nothing known about", target)
        self.network.loadrooturl(target)
        path = entry["id"]
        view = "@@fromFS.snarf?note=%s" % urllib.quote(note)
        if raise_on_conflicts:
            view += "&raise=1"
        head, tail = split(realpath(target))
        data = DataSource(head, tail)
        fp, headers = self.network.httpreq(path, view, data)
        try:
            self.merge_snarffile(fp, head, tail)
        finally:
            fp.close()

    def checkin(self, target, note="fssync_checkin"):
        rootpath = self.network.rootpath
        if not rootpath:
            raise Error("root url not set")
        if rootpath == "/":
            raise Error("root url should name an inferior object")
        i = rootpath.rfind("/")
        path, name = rootpath[:i], rootpath[i+1:]
        if not path:
            path = "/"
        if not name:
            raise Error("root url should not end in '/'")
        entry = self.metadata.getentry(target)
        if not entry:
            raise Error("nothing known about", target)
        qnote = urllib.quote(note)
        qname = urllib.quote(name)
        head, tail = split(realpath(target))
        qsrc = urllib.quote(tail)
        view = "@@checkin.snarf?note=%s&name=%s&src=%s" % (qnote, qname, qsrc)
        data = DataSource(head, tail)
        fp, headers = self.network.httpreq(path, view, data,
                                           expected_type=None)
        message = self.network.slurptext(fp, headers)
        if message:
            print message

    def update(self, target):
        entry = self.metadata.getentry(target)
        if not entry:
            raise Error("nothing known about", target)
        self.network.loadrooturl(target)
        head, tail = fsutil.split(target)
        path = entry["id"]
        fp, headers = self.network.httpreq(path, "@@toFS.snarf")
        try:
            self.merge_snarffile(fp, head, tail)
        finally:
            fp.close()

    def merge(self, args):
        source = args[0]
        if len(args) == 1:
            target = os.curdir
        else:
            target = args[1]

        # make sure that we're merging from compatible directories
        if not self.metadata.getentry(target):
            names = self.metadata.getnames(target)
            if len(names) == 1:
                target = join(target, names[0])
        target_entry = self.metadata.getentry(target)
        if not target_entry:
            print 'Target must be a fssync checkout directory'
            return
        if not self.metadata.getentry(source):
            names = self.metadata.getnames(source)
            if len(names) == 1:
                source = join(source, names[0])
        source_entry = self.metadata.getentry(source)
        if not source_entry:
            print 'Source must be a fssync checkout directory'
            return
        if source_entry[u'id'] != target_entry[u'id']:
            print 'Cannot merge from %s to %s' % (source_entry[u'id'],
                                                  target_entry[u'id'])
            return

        zope.app.fssync.merge.merge(os.path.abspath(source),
                                    os.path.abspath(target), self)
        print 'All done.'


    def merge_snarffile(self, fp, localdir, tail):
        uns = Unsnarfer(fp)
        tmpdir = tempfile.mktemp()
        try:
            os.mkdir(tmpdir)
            uns.unsnarf(tmpdir)
            self.fsmerger.merge(join(localdir, tail), join(tmpdir, tail))
            self.metadata.flush()
            print "All done."
        finally:
            if isdir(tmpdir):
                shutil.rmtree(tmpdir)

    def resolve(self, target):
        entry = self.metadata.getentry(target)
        if "conflict" in entry:
            del entry["conflict"]
            self.metadata.flush()
        elif isdir(target):
            self.dirresolve(target)

    def dirresolve(self, target):
        assert isdir(target)
        names = self.metadata.getnames(target)
        for name in names:
            t = join(target, name)
            e = self.metadata.getentry(t)
            if e:
                self.resolve(t)

    def revert(self, target):
        entry = self.metadata.getentry(target)
        if not entry:
            raise Error("nothing known about", target)
        flag = entry.get("flag")
        orig = fsutil.getoriginal(target)
        if flag == "added":
            entry.clear()
        elif flag == "removed":
            if exists(orig):
                shutil.copyfile(orig, target)
            del entry["flag"]
        elif "conflict" in entry:
            if exists(orig):
                shutil.copyfile(orig, target)
            del entry["conflict"]
        elif isfile(orig):
            if filecmp.cmp(target, orig, shallow=False):
                return
            shutil.copyfile(orig, target)
        elif isdir(target):
            # TODO: how to recurse?
            self.dirrevert(target)
        self.metadata.flush()
        if os.path.isdir(target):
            target = join(target, "")
        self.reporter("Reverted " + target)

    def dirrevert(self, target):
        assert isdir(target)
        names = self.metadata.getnames(target)
        for name in names:
            t = join(target, name)
            e = self.metadata.getentry(t)
            if e:
                self.revert(t)

    def reporter(self, msg):
        if msg[0] not in "/*":
            print msg.encode('utf-8') # uo: is encode needed here?

    def diff(self, target, mode=1, diffopts="", need_original=True):
        assert mode == 1, "modes 2 and 3 are not yet supported"
        entry = self.metadata.getentry(target)
        if not entry:
            raise Error("diff target '%s' doesn't exist", target)
        if "flag" in entry and need_original:
            raise Error("diff target '%s' is added or deleted", target)
        if isdir(target):
            self.dirdiff(target, mode, diffopts, need_original)
            return
        orig = fsutil.getoriginal(target)
        if not isfile(target):
            if entry.get("flag") == "removed":
                target = DEV_NULL
            else:
                raise Error("diff target '%s' is file nor directory", target)
        have_original = True
        if not isfile(orig):
            if entry.get("flag") != "added":
                raise Error("can't find original for diff target '%s'", target)
            have_original = False
            orig = DEV_NULL
        if have_original and filecmp.cmp(target, orig, shallow=False):
            return
        print "Index:", target
        sys.stdout.flush()
        cmd = ("diff %s %s %s" % (diffopts, quote(orig), quote(target)))
        os.system(cmd)

    def dirdiff(self, target, mode=1, diffopts="", need_original=True):
        assert isdir(target)
        names = self.metadata.getnames(target)
        for name in names:
            t = join(target, name)
            e = self.metadata.getentry(t)
            if e and (("flag" not in e) or not need_original):
                self.diff(t, mode, diffopts, need_original)

    def add(self, path, type=None, factory=None):
        entry = self.basicadd(path, type, factory)
        head, tail = fsutil.split(path)
        pentry = self.metadata.getentry(head)
        if not pentry:
            raise Error("can't add '%s': its parent is not registered", path)
        if "id" not in pentry:
            raise Error("can't add '%s': its parent has no 'id' key", path)
        zpath = fsutil.encode(pentry["id"])
        if not zpath.endswith("/"):
            zpath += "/"
        zpath += tail
        entry["id"] = zpath
        self.metadata.flush()
        if isdir(path):
            # Force Entries.xml to exist, even if it wouldn't normally
            zopedir = join(path, "@@Zope")
            efile = join(zopedir, "Entries.xml")
            if not exists(efile):
                if not exists(zopedir):
                    os.makedirs(zopedir)
                    self.network.writefile(dump_entries({}), efile)
            print "A", join(path, "")
        else:
            print "A", path

    def basicadd(self, path, type=None, factory=None):
        if not exists(path):
            raise Error("nothing known about '%s'", path)
        entry = self.metadata.getentry(path)
        if entry:
            raise Error("object '%s' is already registered", path)
        entry["flag"] = "added"
        if type:
            entry["type"] = type
        if factory:
            entry["factory"] = factory
        return entry

    def copy(self, src, dst=None, children=True):
        if not exists(src):
            raise Error("%s does not exist" % src)
        dst = dst or ''
        if (not dst) or isdir(dst):
            target_dir = dst
            target_name = basename(os.path.abspath(src))
        else:
            target_dir, target_name = os.path.split(dst)
            if target_dir:
                if not exists(target_dir):
                    raise Error("destination directory does not exist: %r"
                                % target_dir)
                if not isdir(target_dir):
                    import errno
                    err = IOError(errno.ENOTDIR, "Not a directory", target_dir)
                    raise Error(str(err))
        if not self.metadata.getentry(target_dir):
            raise Error("nothing known about '%s'" % target_dir)
        srcentry = self.metadata.getentry(src)
        from zope.fssync import copier
        if srcentry:
            # already known to fssync; we need to deal with metadata,
            # Extra, and Annotations
            copier = copier.ObjectCopier(self)
        else:
            copier = copier.FileCopier(self)
        copier.copy(src, join(target_dir, target_name), children)

    def mkdir(self, path):
        dir, name = split(path)
        if dir:
            if not exists(dir):
                raise Error("directory %r does not exist" % dir)
            if not isdir(dir):
                raise Error("%r is not a directory" % dir)
        else:
            dir = os.curdir
        entry = self.metadata.getentry(dir)
        if not entry:
            raise Error("know nothing about container for %r" % path)
        if exists(path):
            raise Error("%r already exists" % path)
        os.mkdir(path)
        self.add(path)

    def remove(self, path):
        if exists(path):
            raise Error("'%s' still exists", path)
        entry = self.metadata.getentry(path)
        if not entry:
            raise Error("nothing known about '%s'", path)
        zpath = entry.get("id")
        if not zpath:
            raise Error("can't remote '%s': its zope path is unknown", path)
        if entry.get("flag") == "added":
            entry.clear()
        else:
            entry["flag"] = "removed"
        self.metadata.flush()
        print "R", path

    def status(self, target, descend_only=False, verbose=True):
        entry = self.metadata.getentry(target)
        flag = entry.get("flag")
        if isfile(target):
            if not entry:
                if not self.fsmerger.ignore(target):
                    print "?", target
            elif flag == "added":
                print "A", target
            elif flag == "removed":
                print "R(reborn)", target
            else:
                original = fsutil.getoriginal(target)
                if isfile(original):
                    if filecmp.cmp(target, original):
                        if verbose:
                            print "=", target
                    else:
                        print "M", target
                else:
                    print "M(lost-original)", target
        elif isdir(target):
            pname = join(target, "")
            if not entry:
                if not descend_only and not self.fsmerger.ignore(target):
                    print "?", pname
            elif flag == "added":
                print "A", pname
            elif flag == "removed":
                print "R(reborn)", pname
            elif verbose:
                print "/", pname
            if entry:
                # Recurse down the directory
                namesdir = {}
                for name in os.listdir(target):
                    ncname = normcase(name)
                    if ncname != fsutil.nczope:
                        namesdir[ncname] = name
                for name in self.metadata.getnames(target):
                    ncname = normcase(name)
                    namesdir[ncname] = name
                ncnames = namesdir.keys()
                ncnames.sort()
                for ncname in ncnames:
                    self.status(join(target, namesdir[ncname]),
                                verbose=verbose)
        elif exists(target):
            if not entry:
                if not self.fsmerger.ignore(target):
                    print "?", target
            elif flag:
                print flag[0].upper() + "(unrecognized)", target
            else:
                print "M(unrecognized)", target
        else:
            if not entry:
                print "nonexistent", target
            elif flag == "removed":
                print "R", target
            elif flag == "added":
                print "A(lost)", target
            else:
                print "lost", target
        annotations = fsutil.getannotations(target)
        if isdir(annotations):
            self.status(annotations, True, verbose=verbose)
        extra = fsutil.getextra(target)
        if isdir(extra):
            self.status(extra, True, verbose=verbose)

def quote(s):
    """Helper to put quotes around arguments passed to shell if necessary."""
    if os.name == "posix":
        meta = "\\\"'*?[&|()<>`#$; \t\n"
    else:
        meta = " "
    needquotes = False
    for c in meta:
        if c in s:
            needquotes = True
            break
    if needquotes:
        if os.name == "posix":
            # use ' to quote, replace ' by '"'"'
            s = "'" + s.replace("'", "'\"'\"'") + "'"
        else:
            # (Windows) use " to quote, replace " by ""
            s = '"' + s.replace('"', '""') + '"'
    return s
