#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#              Ethernet over WebSocket tunneling server/client
#
# depends on:
#   - python-2.7.2
#   - python-pytun-0.2
#   - websocket-client-0.7.0
#   - tornado-2.2.1
#
# todo:
#   - servant mode support (like typical p2p software)
#
# ===========================================================================
# Copyright (c) 2012, Atzm WATANABE <atzm@atzm.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===========================================================================
#
# $Id: etherws.py 160 2012-05-19 17:39:34Z atzm $

import os
import sys
import ssl
import time
import base64
import hashlib
import getpass
import argparse
import threading

import pytun
import websocket
import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver


class DebugMixIn(object):
    def dprintf(self, msg, *args):
        if self._debug:
            prefix = '[%s] %s - ' % (time.asctime(), self.__class__.__name__)
            sys.stderr.write(prefix + (msg % args))


class TapHandler(DebugMixIn):
    def __init__(self, dev, debug=False):
        self._debug = debug
        self._clients = []
        self._tap = pytun.TunTapDevice(dev, pytun.IFF_TAP | pytun.IFF_NO_PI)
        self._tap.up()
        self._glock = threading.Lock()

    def fileno(self):
        with self._glock:
            return self._tap.fileno()

    def register_client(self, client):
        with self._glock:
            self._clients.append(client)

    def unregister_client(self, client):
        with self._glock:
            self._clients.remove(client)

    def write(self, caller, message):
        with self._glock:
            clients = self._clients[:]

            if caller is not self:
                clients.remove(caller)
                self._tap.write(message)

            for c in clients:
                c.write_message(message, True)

    def __call__(self, fd, events):
        with self._glock:
            data = self._tap.read(self._tap.mtu)
        self.write(self, data)


class EtherWebSocketHandler(tornado.websocket.WebSocketHandler, DebugMixIn):
    def __init__(self, app, req, tap, debug=False):
        super(EtherWebSocketHandler, self).__init__(app, req)
        self._tap = tap
        self._debug = debug

    def open(self):
        self._tap.register_client(self)
        self.dprintf('connected: %s\n', self.request.remote_ip)

    def on_message(self, message):
        self._tap.write(self, message)
        self.dprintf('received: %s %s\n',
                     self.request.remote_ip, message.encode('hex'))

    def on_close(self):
        self._tap.unregister_client(self)
        self.dprintf('disconnected: %s\n', self.request.remote_ip)


class EtherWebSocketClient(DebugMixIn):
    def __init__(self, tap, url, user=None, passwd=None, debug=False):
        self._sock = None
        self._tap = tap
        self._url = url
        self._debug = debug
        self._options = {}

        if user and passwd:
            token = base64.b64encode('%s:%s' % (user, passwd))
            auth = ['Authorization: Basic %s' % token]
            self._options['header'] = auth

    @property
    def closed(self):
        return not self._sock

    def open(self):
        if not self.closed:
            raise websocket.WebSocketException('already opened')
        self._sock = websocket.WebSocket()
        self._sock.connect(self._url, **self._options)
        self.dprintf('connected: %s\n', self._url)

    def close(self):
        if self.closed:
            raise websocket.WebSocketException('already closed')
        self._sock.close()
        self._sock = None
        self.dprintf('disconnected: %s\n', self._url)

    def write_message(self, message, binary=False):
        if self.closed:
            raise websocket.WebSocketException('closed socket')
        if binary:
            flag = websocket.ABNF.OPCODE_BINARY
        else:
            flag = websocket.ABNF.OPCODE_TEXT
        self._sock.send(message, flag)
        self.dprintf('sent: %s %s\n', self._url, message.encode('hex'))

    def run_forever(self):
        try:
            if self.closed:
                self.open()
            while True:
                data = self._sock.recv()
                if data is None:
                    break
                self._tap.write(self, data)
        finally:
            self.close()


def daemonize(nochdir=False, noclose=False):
    if os.fork() > 0:
        sys.exit(0)

    os.setsid()

    if os.fork() > 0:
        sys.exit(0)

    if not nochdir:
        os.chdir('/')

    if not noclose:
        os.umask(0)
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        os.close(0)
        os.close(1)
        os.close(2)
        sys.stdin = open(os.devnull)
        sys.stdout = open(os.devnull, 'a')
        sys.stderr = open(os.devnull, 'a')


def realpath(ns, *keys):
    for k in keys:
        v = getattr(ns, k, None)
        if v is not None:
            v = os.path.realpath(v)
            setattr(ns, k, v)
            open(v).close()  # check readable
    return ns


def server_main(args):
    def wrap_basic_auth(cls, users):
        o_exec = cls._execute

        if not users:
            return cls

        def execute(self, transforms, *args, **kwargs):
            def auth_required():
                self.stream.write(tornado.escape.utf8(
                    'HTTP/1.1 401 Authorization Required\r\n'
                    'WWW-Authenticate: Basic realm=etherws\r\n\r\n'
                ))
                self.stream.close()

            creds = self.request.headers.get('Authorization')

            if not creds or not creds.startswith('Basic '):
                return auth_required()

            try:
                name, passwd = base64.b64decode(creds[6:]).split(':', 1)
                passwd = base64.b64encode(hashlib.sha1(passwd).digest())

                if name not in users or users[name] != passwd:
                    return auth_required()

                return o_exec(self, transforms, *args, **kwargs)

            except:
                return auth_required()

        cls._execute = execute
        return cls

    def load_htpasswd(path):
        users = {}
        try:
            with open(path) as fp:
                for line in fp:
                    line = line.strip()
                    if 0 <= line.find(':'):
                        name, passwd = line.split(':', 1)
                        if passwd.startswith('{SHA}'):
                            users[name] = passwd[5:]
            if not users:
                raise ValueError('no valid users found')
        except TypeError:
            pass
        return users

    realpath(args, 'keyfile', 'certfile', 'htpasswd')

    if args.keyfile and args.certfile:
        ssl_options = {'keyfile': args.keyfile, 'certfile': args.certfile}
    elif args.keyfile or args.certfile:
        raise ValueError('both keyfile and certfile are required')
    else:
        ssl_options = None

    if args.port is None:
        if ssl_options:
            args.port = 443
        else:
            args.port = 80
    elif not (0 <= args.port <= 65535):
        raise ValueError('invalid port: %s' % args.port)

    handler = wrap_basic_auth(EtherWebSocketHandler,
                              load_htpasswd(args.htpasswd))

    tap = TapHandler(args.device, debug=args.debug)
    app = tornado.web.Application([
        (args.path, handler, {'tap': tap, 'debug': args.debug}),
    ])
    server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    server.listen(args.port, address=args.address)

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(tap.fileno(), tap, ioloop.READ)

    if not args.foreground:
        daemonize()

    ioloop.start()


def client_main(args):
    realpath(args, 'cacerts')

    if args.debug:
        websocket.enableTrace(True)

    if not args.insecure:
        websocket._SSLSocketWrapper = \
            lambda s: ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED,
                                      ca_certs=args.cacerts)

    if args.user and args.passwd is None:
        args.passwd = getpass.getpass()

    tap = TapHandler(args.device, debug=args.debug)
    client = EtherWebSocketClient(tap, args.uri,
                                  args.user, args.passwd, args.debug)

    tap.register_client(client)
    client.open()

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(tap.fileno(), tap, ioloop.READ)

    t = threading.Thread(target=ioloop.start)
    t.setDaemon(True)

    if not args.foreground:
        daemonize()

    t.start()
    client.run_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', action='store', default='ethws%d')
    parser.add_argument('--foreground', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_s = subparsers.add_parser('server')
    parser_s.add_argument('--address', action='store', default='')
    parser_s.add_argument('--port', action='store', type=int)
    parser_s.add_argument('--path', action='store', default='/')
    parser_s.add_argument('--htpasswd', action='store')
    parser_s.add_argument('--keyfile', action='store')
    parser_s.add_argument('--certfile', action='store')

    parser_c = subparsers.add_parser('client')
    parser_c.add_argument('--uri', action='store', required=True)
    parser_c.add_argument('--insecure', action='store_true', default=False)
    parser_c.add_argument('--cacerts', action='store')
    parser_c.add_argument('--user', action='store')
    parser_c.add_argument('--passwd', action='store')

    args = parser.parse_args()

    if args.subcommand == 'server':
        server_main(args)
    elif args.subcommand == 'client':
        client_main(args)


if __name__ == '__main__':
    main()
