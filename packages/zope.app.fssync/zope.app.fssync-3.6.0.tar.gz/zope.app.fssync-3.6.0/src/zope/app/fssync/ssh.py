##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
import getpass
import httplib
import os.path
import socket
import paramiko
import sys


class FileSocket(object):
    """
    Adapts a file to the socket interface for use with http.HTTPResponse
    """
    def __init__(self, file):
        self.file = file

    def makefile(self, *args):
        return self.file


class ConfirmationPolicy(paramiko.WarningPolicy, paramiko.RejectPolicy, paramiko.AutoAddPolicy):
    def _add_key(self, client, hostname, key):
        paramiko.AutoAddPolicy.missing_host_key(self, client, hostname, key)
        client.save_host_keys(SSHConnection.key_file_name)

    def missing_host_key(self, client, hostname, key):
        paramiko.WarningPolicy.missing_host_key(self, client, hostname, key)
        answer = raw_input("Are you sure you want to continue connecting (yes/no)? ")
        yes_no = {'no': paramiko.RejectPolicy.missing_host_key,
                  'yes': ConfirmationPolicy._add_key,}
        while answer.lower() not in yes_no:
            print "Please type 'yes' or 'no'."
            answer = raw_input("Are you sure you want to continue connecting (yes/no)? ")
        return yes_no[answer.lower()](self, client, hostname, key)


class SSHConnection(object):
    """
    SSH connection that implements parts of the httplib.HTTPConnection
    interface
    """
    if sys.platform == 'win32':
        sys_key_file_name = os.path.expanduser('~/ssh/known_hosts')
        key_file_name = os.path.expanduser('~/ssh/fssync_known_hosts')
    else:
        sys_key_file_name = os.path.expanduser('~/.ssh/known_hosts')
        key_file_name = os.path.expanduser('~/.ssh/fssync_known_hosts')

    # This and the __new__ method are to ensure that the SSHConnection doesn't
    # get garbage collected by paramiko too early.
    clients = {}

    def __new__(cls, host_port, user_passwd=None):
        if host_port in cls.clients:
            return cls.clients[host_port]
        else:
            cls.clients[host_port] = object.__new__(
                cls, host_port, user_passwd)
            return cls.clients[host_port]

    def __init__(self, host_port, user_passwd=None):
        if not hasattr(self, 'headers'):
            self.headers = {}
            self.host, self.port = host_port.split(':')
            self.port = int(self.port)

            # if username is specified in URL then use it, otherwise
            # default to local userid
            if user_passwd:
                self.remote_user_name = user_passwd.split(':')[0]
            else:
                self.remote_user_name = getpass.getuser()
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(ConfirmationPolicy())
            self.client.load_system_host_keys(self.sys_key_file_name)
            try:
                self.client.load_host_keys(self.key_file_name)
            except IOError, ioe:
                # This will get handled later in the ConfirmationPolicy.  We can
                # pass for now.
                pass
            try:
                self.client.connect(self.host, self.port, self.remote_user_name)
            except paramiko.PasswordRequiredException, pre:
                password = getpass.getpass("Password to unlock password-protected key? ")
                self.client.connect(
                    self.host, self.port, self.remote_user_name, password=password)


    def putrequest(self, method, path):
        # start zsync subsystem on server
        self.channel = self.client.get_transport().open_session()
        self.channel.invoke_subsystem('zsync')
        self.channelr = self.channel.makefile('rb')
        self.channelw = self.channel.makefile('wb')

        # start sending request
        self.channelw.write('%s %s\r\n' % (method, path))


    def putheader(self, name, value):
        self.channelw.write('%s: %s\r\n' % (name, value))

    def endheaders(self):
        self.channelw.write('\r\n')

    def send(self, data):
        self.channelw.write(data)

    def getresponse(self):
        response = httplib.HTTPResponse(FileSocket(self.channelr))
        response.begin()
        return response
