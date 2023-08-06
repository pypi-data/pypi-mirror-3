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
# $Id: etherws.py 151 2012-05-15 23:56:50Z atzm $

import os
import sys
import base64
import hashlib
import getpass
import argparse
import threading

import pytun
import websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket


class TapHandler(object):
    def __init__(self, dev, debug=False):
        self._debug = debug
        self._clients = []
        self._tap = pytun.TunTapDevice(dev, pytun.IFF_TAP | pytun.IFF_NO_PI)
        self._tap.up()
        self._write_lock = threading.Lock()

    def fileno(self):
        return self._tap.fileno()

    def register_client(self, client):
        self._clients.append(client)

    def unregister_client(self, client):
        self._clients.remove(client)

    def write(self, caller, message):
        if self._debug:
            sys.stderr.write('%s: %s\n' % (caller.__class__.__name__,
                                           message.encode('hex')))
        try:
            self._write_lock.acquire()

            clients = self._clients[:]

            if caller is not self:
                clients.remove(caller)
                self._tap.write(message)

            for c in clients:
                c.write_message(message, True)

        finally:
            self._write_lock.release()

    def __call__(self, fd, events):
        self.write(self, self._tap.read(self._tap.mtu))


class EtherWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, app, req, tap, debug=False):
        super(EtherWebSocket, self).__init__(app, req)
        self._tap = tap
        self._debug = debug

    def open(self):
        self._tap.register_client(self)

    def on_message(self, message):
        self._tap.write(self, message)

    def on_close(self):
        self._tap.unregister_client(self)


class  EtherWebSocketClient(object):
    def __init__(self, tap, url, user=None, passwd=None):
        self._sock = None
        self._tap = tap
        self._url = url
        self._options = {}

        if user and passwd:
            token = base64.b64encode('%s:%s' % (user, passwd))
            auth = ['Authorization: Basic %s' % token]
            self._options['header'] = auth

    def open(self):
        self._sock = websocket.WebSocket()
        self._sock.connect(self._url, **self._options)

    def close(self):
        self._sock.close()
        self._sock = None

    def write_message(self, message, binary=False):
        flag = websocket.ABNF.OPCODE_TEXT
        if binary:
            flag = websocket.ABNF.OPCODE_BINARY
        self._sock.send(message, flag)

    def run_forever(self):
        try:
            if not self._sock:
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


def server_main(args):
    def may_auth_required(cls, users):
        if not users:
            return cls

        orig_execute = cls._execute

        def _execute(self, transforms, *args, **kwargs):
            def auth_required():
                self.stream.write(tornado.escape.utf8(
                    'HTTP/1.1 401 Authorization Required\r\n'
                    'WWW-Authenticate: Basic realm=etherws\r\n\r\n'
                ))
                self.stream.close()

            try:
                creds = self.request.headers.get('Authorization')

                if not creds or not creds.startswith('Basic '):
                    return auth_required()

                creds = base64.b64decode(creds[6:])

                if creds.find(':') < 0:
                    return auth_required()

                name, passwd = creds.split(':', 2)
                passwd = base64.b64encode(hashlib.sha1(passwd).digest())

                if name not in users or users[name] != passwd:
                    return auth_required()

                return orig_execute(self, transforms, *args, **kwargs)

            except:
                return auth_required()

        cls._execute = _execute
        return cls

    def load_htpasswd(path):
        users = {}
        try:
            with open(path) as fp:
                for line in fp:
                    line = line.strip()
                    if 0 <= line.find(':'):
                        name, passwd = line.split(':', 2)
                        if passwd.startswith('{SHA}'):
                            users[name] = passwd[5:]
        except TypeError:
            pass
        return users

    handler = may_auth_required(EtherWebSocket, load_htpasswd(args.htpasswd))
    ssl_options = {}

    for k in ['keyfile', 'certfile']:
        v = getattr(args, k, None)
        if v:
            v = os.path.realpath(v)
            ssl_options[k] = v
            open(v).close()  # readable test

    if len(ssl_options) == 1:
        raise ValueError('both keyfile and certfile are required')
    elif not ssl_options:
        ssl_options = None

    if not args.port:
        if ssl_options:
            args.port = 443
        else:
            args.port = 80

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
    if args.debug:
        websocket.enableTrace(True)

    passwd = None
    if args.user:
        passwd = getpass.getpass()

    tap = TapHandler(args.device, debug=args.debug)
    client = EtherWebSocketClient(tap, args.uri, args.user, passwd)

    tap.register_client(client)
    client.open()

    t = threading.Thread(target=client.run_forever)
    t.setDaemon(True)

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(tap.fileno(), tap, ioloop.READ)

    if not args.foreground:
        daemonize()

    t.start()
    ioloop.start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', action='store', default='ethws%d')
    parser.add_argument('--foreground', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_server = subparsers.add_parser('server')
    parser_server.add_argument('--address', action='store', default='')
    parser_server.add_argument('--port', action='store', type=int)
    parser_server.add_argument('--path', action='store', default='/')
    parser_server.add_argument('--htpasswd', action='store')
    parser_server.add_argument('--keyfile', action='store')
    parser_server.add_argument('--certfile', action='store')

    parser_client = subparsers.add_parser('client')
    parser_client.add_argument('--uri', action='store', required=True)
    parser_client.add_argument('--user', action='store')

    args = parser.parse_args()

    if args.subcommand == 'server':
        server_main(args)
    elif args.subcommand == 'client':
        client_main(args)


if __name__ == '__main__':
    main()
