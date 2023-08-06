Introduction
============
etherws is an implementation of Ethernet over WebSocket tunnel
based on Linux Universal TUN/TAP device driver.

How to Use
==========
For example, if you want to make virtual ethernet link for *VM1* and *VM2*
whose hypervisor's broadcast domains were split by router *R*::

  +------------------+            +------------------+
  | Hypervisor1      |            |      Hypervisor2 |
  |  +-----+         |            |         +-----+  |
  |  | VM1 |         |            |         | VM2 |  |
  |  +--+--+         |            |         +--+--+  |
  |     | (vnet0)    |            |    (vnet0) |     |
  |  +--+--+         |            |         +--+--+  |
  |  | br0 |         |            |         | br0 |  |
  |  +--+--+         |            |         +--+--+  |
  |     |            |            |            |     |
  | (ethws0)  (eth0) |            | (eth0)  (ethws0) |
  +----||--------+---+            +----+-------||----+
       ||        |        +---+        |       ||
       ||   -----+--------| R |--------+-----  ||
       ||                 +---+                ||
       ||                                      ||
       ``======================================''
            (Ethernet over WebSocket tunnel)

then you can use following commands.

on *Hypervisor1*::

  # etherws server
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

on *Hypervisor2*::

  # etherws client --uri ws://<Hypervisor1's IP address>/
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

If connection through the tunnel is unstable, then you may fix it
by changing VM's MTU to under 1500, e.g.::

  # ifconfig eth0 mtu 1400

Tunnel Encryption
=================
etherws supports SSL/TLS connection (but client does not verify server
certificates).
If you want to encrypt the tunnel, then you can use following options.

on *Hypervisor1* (options *keyfile* and *certfile* were specified)::

  # etherws server --keyfile ssl.key --certfile ssl.crt

on *Hypervisor2* (option *uri*'s scheme was changed to *wss*)::

  # etherws client --uri wss://<Hypervisor1's IP address>/

You also can test by following command::

  # openssl s_client -connect <Hypervisor1's IP address>:443

Client Authentication
=====================
etherws supports HTTP Basic Authentication.
It means you can use etherws as simple L2-VPN server/client.

On server side, etherws requires user information in Apache htpasswd
format (and currently supports SHA-1 digest only). To create this file::

  # htpasswd -s -c filename username

If you do not have htpasswd command, then you can use python one-liner::

  # python -c 'import hashlib; print("username:{SHA}" + hashlib.sha1("password").digest().encode("base64"))'

To run server with this::

  # etherws server --htpasswd filename

You also can test by following command::

  # telnet <address> 80
  GET / HTTP/1.1

It will return *401 Authorization Required*.

On client side, etherws requires username as option, and password from
stdin::

  # etherws client --uri ws://<address>/ --user username
  Password: 

If authentication did not succeed, then it will die with some error messages.

Note that you should not use HTTP Basic Authentication without SSL/TLS
support, because it is insecure in itself.

History
=======
0.3 (2012-05-17 JST)
  - client authentication support

0.2 (2012-05-16 JST)
  - SSL/TLS connection support

0.1 (2012-05-15 JST)
  - First release
