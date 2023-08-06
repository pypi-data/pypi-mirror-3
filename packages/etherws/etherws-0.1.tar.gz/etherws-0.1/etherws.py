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
#   - SSL support
#   - servant mode (like typical p2p software)
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
# $Id: etherws.py 141 2012-05-15 08:22:21Z atzm $

import os
import sys
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
    tap = TapHandler(args.device, debug=args.debug)
    app = tornado.web.Application([
        (args.path, EtherWebSocket, {'tap': tap, 'debug': args.debug}),
    ])
    server = tornado.httpserver.HTTPServer(app)
    server.listen(args.port, address=args.address)

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(tap.fileno(), tap, ioloop.READ)
    ioloop.start()


def client_main(args):
    if args.debug:
        websocket.enableTrace(True)

    tap = TapHandler(args.device, debug=args.debug)
    client = websocket.WebSocketApp(args.uri)
    client.on_message = lambda s, m: tap.write(client, m)
    client.write_message = \
        lambda m, b: client.sock.send(m, websocket.ABNF.OPCODE_BINARY)
    tap.register_client(client)

    t = threading.Thread(target=client.run_forever)
    t.setDaemon(True)
    t.start()

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(tap.fileno(), tap, ioloop.READ)
    ioloop.start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', action='store', default='ethws%d')
    parser.add_argument('--foreground', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_server = subparsers.add_parser('server')
    parser_server.add_argument('--address', action='store', default='')
    parser_server.add_argument('--port', action='store', type=int, default=80)
    parser_server.add_argument('--path', action='store', default='/')

    parser_client = subparsers.add_parser('client')
    parser_client.add_argument('--uri', action='store', required=True)

    args = parser.parse_args()

    if not args.foreground:
        daemonize()

    if args.subcommand == 'server':
        server_main(args)
    elif args.subcommand == 'client':
        client_main(args)


if __name__ == '__main__':
    main()
