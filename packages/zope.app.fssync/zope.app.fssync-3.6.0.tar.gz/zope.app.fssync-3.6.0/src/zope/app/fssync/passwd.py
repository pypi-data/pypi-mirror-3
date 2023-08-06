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
"""Password manager for fssync clients.

$Id: passwd.py 25177 2004-06-02 13:17:31Z jim $
"""

import base64
import httplib
import os

from cStringIO import StringIO

from zope.fssync import fsutil

DEFAULT_FILENAME = os.path.expanduser(os.path.join("~", ".zsyncpass"))


class PasswordManager(object):
    """Manager for a cache of basic authentication tokens for zsync.

    This stores tokens in a file, and allows them to be retrieved by
    the zsync application.  The tokens are stored in their 'cooked'
    form, so while someone could easily decode them or use them to
    make requests, the casual reader won't be able to use them easily.

    The cache file is created with restricted permissions, so other
    users should not be able to read it unless the permissions are
    modified.
    """

    def __init__(self, filename=None):
        if not filename:
            filename = DEFAULT_FILENAME
        self.authfile = filename

    def getPassword(self, user, host_port):
        """Read a password from the user."""
        import getpass
        prompt = "Password for %s at %s: " % (user, host_port)
        return getpass.getpass(prompt)

    def createToken(self, user_passwd):
        """Generate a basic authentication token from 'user:password'."""
        return base64.encodestring(user_passwd).strip()

    def getToken(self, scheme, host_port, user):
        """Get an authentication token for the user for a specific server.

        If a corresponding token exists in the cache, that is retured,
        otherwise the user is prompted for their password and a new
        token is generated.  A new token is not automatically stored
        in the cache.
        """
        host_port = _normalize_host(scheme, host_port)
        prefix = [scheme, host_port, user]

        if os.path.exists(self.authfile):
            f = open(self.authfile, "r")
            try:
                for line in f:
                    line = line.strip()
                    if line[:1] in ("#", ""):
                        continue
                    parts = line.split()
                    if parts[:3] == prefix:
                        return parts[3]
            finally:
                f.close()

        # not in ~/.zsyncpass
        pw = self.getPassword(user, host_port)
        user_passwd = "%s:%s" % (user, pw)
        return self.createToken(user_passwd)

    def addToken(self, scheme, host_port, user, token):
        """Add a token to the persistent cache.

        If a corresponding token already exists in the cache, it is
        replaced.
        """
        host_port = _normalize_host(scheme, host_port)
        record = "%s %s %s %s\n" % (scheme, host_port, user, token)

        if os.path.exists(self.authfile):
            prefix = [scheme, host_port, user]
            f = open(self.authfile)
            sio = StringIO()
            found = False
            for line in f:
                parts = line.split()
                if parts[:3] == prefix:
                    sio.write(record)
                    found = True
                else:
                    sio.write(line)
            f.close()
            if not found:
                sio.write(record)
            text = sio.getvalue()
        else:
            text = record
        f = self.createAuthFile()
        f.write(text)
        f.close()

    def removeToken(self, scheme, host_port, user):
        """Remove a token from the authentication database.

        Returns True if a token was found and removed, or False if no
        matching token was found.

        If the resulting cache file contains only blank lines, it is
        removed.
        """
        if not os.path.exists(self.authfile):
            return False
        host_port = _normalize_host(scheme, host_port)
        prefix = [scheme, host_port, user]
        found = False
        sio = StringIO()
        f = open(self.authfile)
        nonblank = False
        for line in f:
            parts = line.split()
            if parts[:3] == prefix:
                found = True
            else:
                if line.strip():
                    nonblank = True
                sio.write(line)
        f.close()
        if found:
            if nonblank:
                text = sio.getvalue()
                f = self.createAuthFile()
                f.write(text)
                f.close()
            else:
                # nothing left in the file but blank lines; remove it
                os.unlink(self.authfile)
        return found

    def createAuthFile(self):
        """Create the token cache file with the right permissions."""
        new = not os.path.exists(self.authfile)
        if os.name == "posix":
            old_umask = os.umask(0077)
            try:
                f = open(self.authfile, "w", 0600)
            finally:
                os.umask(old_umask)
        else:
            f = open(self.authfile, "w")
        if new:
            f.write(_NEW_FILE_HEADER)
        return f

_NEW_FILE_HEADER = """\
#
# Stored authentication tokens for zsync.
# Manipulate this data using the 'zsync login' and 'zsync logout';
# read the zsync documentation for more information.
#
"""

def _normalize_host(scheme, host_port):
    if scheme == "http":
        return _normalize_port(host_port, httplib.HTTP_PORT)
    elif scheme == "https":
        return _normalize_port(host_port, httplib.HTTPS_PORT)
    elif scheme == "zsync+ssh":
        return _normalize_port(host_port, None)
    else:
        raise fsutil.Error("unsupported URL scheme: %r" % scheme)

def _normalize_port(host_port, default_port):
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        try:
            port = int(port)
        except ValueError:
            raise fsutil.Error("invalid port specification: %r" % port)
        if port <= 0:
            raise fsutil.Error("invalid port: %d" % port)
        if port == default_port:
            host_port = host
    return host_port.lower()
