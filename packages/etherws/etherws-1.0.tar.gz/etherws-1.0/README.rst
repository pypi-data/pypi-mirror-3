Introduction
============
etherws is an implementation of Ethernet over WebSocket tunnel based on Linux
Universal TUN/TAP device driver.

Overview
========
*etherws sw* acts as a simple virtual ethernet switch, and it can create TAP
interface or WebSocket tunnel by *etherws ctl*::

      [tap]
        |
  +-----+------+   (control)
  | etherws sw | <-----------+
  +-----||-----+             |
        ||            +-------------+
    (WebSocket)       | etherws ctl |
        ||            +-------------+
  +-----||-----+             |
  | etherws sw | <-----------+
  +-----+------+   (control)
        |
      [tap]

Basic Usage
===========
For example, consider creating following simple network::

          (Physical Network)
  -----+-------   //  -------+-----
       | 10.0.0.10           | 10.0.0.5
  +----+-----+         +-----+----+ 
  | NodeA    |         | NodeB    |
  |          |         |          |
  | [ethws0] |         | [ethws0] |
  +----||----+         +----||----+
       || 192.0.2.10/24     || 192.0.2.5/24
       ``===================''
          (WebSocket Tunnel)

In this case, *WebSocket Tunnel* will be created by following commands.

on NodeA::

  # etherws sw
  # etherws ctl addport tap ethws0
  # etherws ctl setif --address 192.0.2.10 --netmask 255.255.255.0 1

on NodeB::

  # etherws sw
  # etherws ctl addport tap ethws0
  # etherws ctl setif --address 192.0.2.5 --netmask 255.255.255.0 1
  # etherws ctl addport client ws://10.0.0.10/

*listport*, *listif* or *listfdb* commands will show you current port list,
interface list, or forwarding database entries::

  # etherws ctl listport
  # etherws ctl listif
  # etherws ctl listfdb

Using SSL/TLS
-------------
etherws supports SSL/TLS connection. Tunnels will be encrypted and server will
be verified by using following options.

On server side::

  # etherws sw --sslkey ssl.key --sslcert ssl.crt

*ssl.key* is a server private key, and *ssl.crt* is a server certificate.

On client side::

  # etherws ctl addport client --cacerts ssl.crt wss://10.0.0.10/

URL scheme was just changed to *wss*, and CA certificate to verify server
certificate was specified.

Client verifies server certificate by default. So, for example, *addport* will
fail if your server uses self-signed certificate and client uses another CA
certificate.

If you want to just encrypt tunnels and do not need to verify server
certificate, then you can use *--insecure* option::

  # etherws ctl addport client --insecure wss://10.0.0.10/

Note: see http://docs.python.org/library/ssl.html for more information about
certificates.

Client Authentication
---------------------
etherws supports HTTP Basic Authentication. It means you can use etherws as
simple L2-VPN server/client.

On server side, etherws requires user informations in Apache htpasswd format
(and currently supports SHA-1 digest only). To create this file::

  # htpasswd -s -c filename username

If you do not have htpasswd command, then you can use python one-liner
instead::

  # python -c 'import hashlib; print("username:{SHA}" + hashlib.sha1("password").digest().encode("base64"))'

To run server with this file::

  # etherws sw --htpasswd filename

On client side, etherws requires username and password from option with
*addport* command::

  # etherws ctl addport client --user username --passwd password ws://10.0.0.10/

Or, password can be input from stdin::

  # etherws ctl addport client --user username ws://10.0.0.10/
  Client Password:

If authentication did not succeed, then *addport* will fail.

Note that you should not use HTTP Basic Authentication without SSL/TLS support,
because it is insecure in itself.

Advanced Usage
==============

Remote Control
--------------
*etherws ctl* controls *etherws sw* by JSON-RPC over HTTP. It means you can
control *etherws sw* from remote node. However, allowing remote control without
careful consideration also allows to attack to your server or network. So
control URL is bound to localhost by default.

If you just want to allow remote control, you can use following options for
example::

  # etherws sw --ctlhost 10.0.0.10 --ctlport 1234

This means allowing remote control from any nodes that can access
10.0.0.10:1234 TCP/IP. Of course it is very dangerous as described above.

Here, *etherws ctl* can control remote *etherws sw* using following option::

  # etherws ctl --ctlurl http://10.0.0.10:1234/ctl ...

*etherws sw* controller supports SSL/TLS connection and client authentication
as well as WebSocket tunnel service.

On server side::

  # etherws sw --ctlhost 10.0.0.10 --ctlport 443 \
               --ctlhtpasswd htpasswd --ctlsslkey ssl.key --ctlsslcert ssl.crt

On client side::

  # etherws ctl --ctlurl https://10.0.0.10/ctl \
                --ctluser username --ctlpasswd password ...

Password can be input from stdin as well as WebSocket tunnel creation.

Note: *etherws ctl* currently cannot verify SSL certificate on controller.

Connect Virtual Machines
------------------------
For example, consider creating following virtual machine network::

  +------------------+             +------------------+
  | HypervisorA      |             |      HypervisorB |
  |  +-----+         |             |         +-----+  |
  |  | VM  |         |             |         | VM  |  |
  |  +--+--+         |             |         +--+--+  |
  |     | (vnet0)    |             |    (vnet0) |     |
  |  +--+--+         |             |         +--+--+  |
  |  | br0 |         |             |         | br0 |  |
  |  +--+--+         |             |         +--+--+  |
  |     |            |             |            |     |
  | (ethws0)  (eth0) |             | (eth0)  (ethws0) |
  +----||--------+---+             +----+-------||----+
       ||        |                      |       ||
       ||   -----+--------  //  --------+-----  ||
       ||           (Physical Network)          ||
       ||                                       ||
       ``=======================================''
                   (WebSocket Tunnel)

In this case, it will be created by following commands.

on HypervisorA::

  # etherws sw
  # etherws ctl addport tap ethws0
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

on HypervisorB::

  # etherws sw
  # etherws ctl addport tap ethws0
  # etherws ctl addport client ws://HypervisorA/
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

History
=======
1.0 (2012-08-18 JST)
  - global architecture change

0.7 (2012-06-29 JST)
  - switching support
  - multiple ports support

0.6 (2012-06-16 JST)
  - improve performance

0.5 (2012-05-20 JST)
  - added passwd option to client mode
  - fixed bug: basic authentication password cannot contain colon
  - fixed bug: client loops meaninglessly even if server stops

0.4 (2012-05-19 JST)
  - server certificate verification support

0.3 (2012-05-17 JST)
  - client authentication support

0.2 (2012-05-16 JST)
  - SSL/TLS connection support

0.1 (2012-05-15 JST)
  - First release
