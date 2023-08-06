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
import httplib
import logging
import socket


import paramiko

logging.basicConfig(level=logging.DEBUG)


class Server(paramiko.ServerInterface):
    """
    Demo server configuration
    """
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        # All public keys are accepted for the demo, in a real server
        # you would probably check public keys against keys of
        # authorized users.
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'publickey'


class ZsyncHandler(paramiko.SubsystemHandler):
    """
    An example handler that forwards request to a zope server over
    HTTP. A real server would probably communicate a different way.
    """
    def parse_request(self, channel, transport):
        f = channel.makefile('r')
        line = f.readline().strip('\r\n')
        command, path = line.split(' ', 1)
        command = command.strip()
        path = path.strip()
        headers = {}
        while transport.is_active:
            line = f.readline().strip('\r\n')
            if not line:
                break
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
        body = ''
        length = int(headers.get('content-length', 0))
        if length:
            body = f.read(length)
        return command, path, headers, body

    def start_subsystem(self, name, transport, channel):
        command, path, headers, body = self.parse_request(channel, transport)
        connection = httplib.HTTPConnection('localhost', 8080)
        if body:
            connection.request(command, path, body=body, headers=headers)
        else:
            connection.request(command, path, headers=headers)
        response = connection.getresponse()
        channel.send('HTTP/1.0 %s %s\r\n' % (
                response.status, response.reason))
        for name, value in response.getheaders():
            channel.send('%s: %s\r\n' % (name, value))
        channel.send('\r\n')
        body = response.read()
        channel.sendall(body)


def main(port=2200):
    # read host keys
    host_key = paramiko.RSAKey(filename = '/etc/ssh/ssh_host_rsa_key')

    # start ssh server, install zsync handler
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(None)
    sock.bind(('', port))
    sock.listen(100)
    while True:
        client, addr = sock.accept()
        client.settimeout(None)
        t = paramiko.Transport(client)
        t.add_server_key(host_key)
        t.set_subsystem_handler('zsync', ZsyncHandler)
        t.start_server(server = Server())
