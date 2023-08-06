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
# $Id: etherws.py 169 2012-06-28 14:12:21Z atzm $

import os
import sys
import ssl
import time
import base64
import hashlib
import getpass
import argparse
import traceback

import websocket
import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from pytun import TunTapDevice, IFF_TAP, IFF_NO_PI


class DebugMixIn(object):
    def dprintf(self, msg, func=lambda: ()):
        if self._debug:
            prefix = '[%s] %s - ' % (time.asctime(), self.__class__.__name__)
            sys.stderr.write(prefix + (msg % func()))


class EthernetFrame(object):
    def __init__(self, data):
        self.data = data

    @property
    def multicast(self):
        return ord(self.data[0]) & 1

    @property
    def dst_mac(self):
        return self.data[:6]

    @property
    def src_mac(self):
        return self.data[6:12]

    @property
    def tagged(self):
        return ord(self.data[12]) == 0x81 and ord(self.data[13]) == 0

    @property
    def vid(self):
        if self.tagged:
            return ((ord(self.data[14]) << 8) | ord(self.data[15])) & 0x0fff
        return -1


class FDB(DebugMixIn):
    def __init__(self, ageout, debug=False):
        self._ageout = ageout
        self._debug = debug
        self._dict = {}

    def lookup(self, frame):
        mac = frame.dst_mac
        vid = frame.vid

        group = self._dict.get(vid, None)
        if not group:
            return None

        entry = group.get(mac, None)
        if not entry:
            return None

        if time.time() - entry['time'] > self._ageout:
            del self._dict[vid][mac]
            if not self._dict[vid]:
                del self._dict[vid]
            self.dprintf('aged out: [%d] %s\n',
                         lambda: (vid, mac.encode('hex')))
            return None

        return entry['port']

    def learn(self, port, frame):
        mac = frame.src_mac
        vid = frame.vid

        if vid not in self._dict:
            self._dict[vid] = {}

        self._dict[vid][mac] = {'time': time.time(), 'port': port}
        self.dprintf('learned: [%d] %s\n',
                     lambda: (vid, mac.encode('hex')))

    def delete(self, port):
        for vid in self._dict.keys():
            for mac in self._dict[vid].keys():
                if self._dict[vid][mac]['port'] is port:
                    del self._dict[vid][mac]
                    self.dprintf('deleted: [%d] %s\n',
                                 lambda: (vid, mac.encode('hex')))
            if not self._dict[vid]:
                del self._dict[vid]


class SwitchingHub(DebugMixIn):
    def __init__(self, fdb, debug=False):
        self._fdb = fdb
        self._debug = debug
        self._ports = []

    def register_port(self, port):
        self._ports.append(port)

    def unregister_port(self, port):
        self._fdb.delete(port)
        self._ports.remove(port)

    def forward(self, src_port, frame):
        try:
            self._fdb.learn(src_port, frame)

            if not frame.multicast:
                dst_port = self._fdb.lookup(frame)

                if dst_port:
                    self._unicast(frame, dst_port)
                    return

            self._broadcast(frame, src_port)

        except:  # ex. received invalid frame
            traceback.print_exc()

    def _unicast(self, frame, port):
        port.write_message(frame.data, True)
        self.dprintf('sent unicast: [%d] %s -> %s\n',
                     lambda: (frame.vid,
                              frame.src_mac.encode('hex'),
                              frame.dst_mac.encode('hex')))

    def _broadcast(self, frame, *except_ports):
        ports = self._ports[:]
        for port in except_ports:
            ports.remove(port)
        for port in ports:
            port.write_message(frame.data, True)
        self.dprintf('sent broadcast: [%d] %s -> %s\n',
                     lambda: (frame.vid,
                              frame.src_mac.encode('hex'),
                              frame.dst_mac.encode('hex')))


class TapHandler(DebugMixIn):
    READ_SIZE = 65535

    def __init__(self, switch, dev, debug=False):
        self._switch = switch
        self._dev = dev
        self._debug = debug
        self._tap = None

    @property
    def closed(self):
        return not self._tap

    def open(self):
        if not self.closed:
            raise ValueError('already opened')
        self._tap = TunTapDevice(self._dev, IFF_TAP | IFF_NO_PI)
        self._tap.up()
        self._switch.register_port(self)

    def close(self):
        if self.closed:
            raise ValueError('I/O operation on closed tap')
        self._switch.unregister_port(self)
        self._tap.close()
        self._tap = None

    def fileno(self):
        if self.closed:
            raise ValueError('I/O operation on closed tap')
        return self._tap.fileno()

    def write_message(self, message, binary=False):
        if self.closed:
            raise ValueError('I/O operation on closed tap')
        self._tap.write(message)

    def __call__(self, fd, events):
        try:
            self._switch.forward(self, EthernetFrame(self._read()))
            return
        except:
            traceback.print_exc()
        tornado.ioloop.IOLoop.instance().stop()

    def _read(self):
        if self.closed:
            raise ValueError('I/O operation on closed tap')
        buf = []
        while True:
            buf.append(self._tap.read(self.READ_SIZE))
            if len(buf[-1]) < self.READ_SIZE:
                break
        return ''.join(buf)


class EtherWebSocketHandler(tornado.websocket.WebSocketHandler, DebugMixIn):
    def __init__(self, app, req, switch, debug=False):
        super(EtherWebSocketHandler, self).__init__(app, req)
        self._switch = switch
        self._debug = debug

    def open(self):
        self._switch.register_port(self)
        self.dprintf('connected: %s\n', lambda: self.request.remote_ip)

    def on_message(self, message):
        self._switch.forward(self, EthernetFrame(message))

    def on_close(self):
        self._switch.unregister_port(self)
        self.dprintf('disconnected: %s\n', lambda: self.request.remote_ip)


class EtherWebSocketClient(DebugMixIn):
    def __init__(self, switch, url, user=None, passwd=None, debug=False):
        self._switch = switch
        self._url = url
        self._debug = debug
        self._sock = None
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
        self._switch.register_port(self)
        self.dprintf('connected: %s\n', lambda: self._url)

    def close(self):
        if self.closed:
            raise websocket.WebSocketException('already closed')
        self._switch.unregister_port(self)
        self._sock.close()
        self._sock = None
        self.dprintf('disconnected: %s\n', lambda: self._url)

    def fileno(self):
        if self.closed:
            raise websocket.WebSocketException('closed socket')
        return self._sock.io_sock.fileno()

    def write_message(self, message, binary=False):
        if self.closed:
            raise websocket.WebSocketException('closed socket')
        if binary:
            flag = websocket.ABNF.OPCODE_BINARY
        else:
            flag = websocket.ABNF.OPCODE_TEXT
        self._sock.send(message, flag)

    def __call__(self, fd, events):
        try:
            data = self._sock.recv()
            if data is not None:
                self._switch.forward(self, EthernetFrame(data))
                return
        except:
            traceback.print_exc()
        tornado.ioloop.IOLoop.instance().stop()


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

    if args.ageout <= 0:
        raise ValueError('invalid ageout: %s' % args.ageout)

    ioloop = tornado.ioloop.IOLoop.instance()
    fdb = FDB(ageout=args.ageout, debug=args.debug)
    switch = SwitchingHub(fdb, debug=args.debug)
    taps = [TapHandler(switch, dev, debug=args.debug) for dev in args.device]

    handler = wrap_basic_auth(EtherWebSocketHandler,
                              load_htpasswd(args.htpasswd))
    app = tornado.web.Application([
        (args.path, handler, {'switch': switch, 'debug': args.debug}),
    ])
    server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    server.listen(args.port, address=args.address)

    for tap in taps:
        tap.open()
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
    else:
        websocket._SSLSocketWrapper = \
            lambda s: ssl.wrap_socket(s)

    if args.user and args.passwd is None:
        args.passwd = getpass.getpass()

    if args.ageout <= 0:
        raise ValueError('invalid ageout: %s' % args.ageout)

    ioloop = tornado.ioloop.IOLoop.instance()
    fdb = FDB(ageout=args.ageout, debug=args.debug)
    switch = SwitchingHub(fdb, debug=args.debug)
    taps = [TapHandler(switch, dev, debug=args.debug) for dev in args.device]

    clients = [EtherWebSocketClient(switch, uri,
                                    args.user, args.passwd, args.debug)
               for uri in args.uri]

    for client in clients:
        client.open()
        ioloop.add_handler(client.fileno(), client, ioloop.READ)

    for tap in taps:
        tap.open()
        ioloop.add_handler(tap.fileno(), tap, ioloop.READ)

    if not args.foreground:
        daemonize()

    ioloop.start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', action='append', default=[])
    parser.add_argument('--ageout', action='store', type=int, default=300)
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
    parser_c.add_argument('--uri', action='append', default=[])
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
