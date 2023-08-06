Introduction
============
etherws is an implementation of Ethernet over WebSocket tunnel
based on Linux Universal TUN/TAP device driver.

Usage
=====
For example, if you want to make virtual ethernet link for VM1 and VM2
whose hypervisor's broadcast domains were split by router R::

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

then you can type following commands.

on Hypervisor1::

  # etherws server
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

on Hypervisor2::

  # etherws client --uri ws://<Hypervisor1's IP address>/
  # brctl addbr br0
  # brctl addif br0 vnet0
  # brctl addif br0 ethws0
  # ifconfig br0 up

History
=======
0.1 (2012-05-15)
  - First release
