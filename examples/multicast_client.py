#!/usr/bin/env python3

"""
Send/receive UDP multicast packets.
Requires that your OS kernel supports IP multicast.

Usage:
  mcast -sock (sender, IPv4)
  mcast -sock -6 (sender, IPv6)
  mcast    (receivers, IPv4)
  mcast  -6  (receivers, IPv6)
"""

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'

import time
import struct
import sys

import curio
from curio import socket

socks = set()

async def close(socks):
    for sock in socks:
        await sock.close()

async def main(group):
    # Look up multicast group address in name server and find out IP version
    addrinfo = (await socket.getaddrinfo(group, None))[0]

    # Create a socket
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    socks.add(sock)

    # Allow multiple copies of this program on one machine
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    sock.bind(('', MYPORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    
    if addrinfo[0] == socket.AF_INET6: # IPv6
        # Join group
        mreq = group_bin + struct.pack('@I', 0)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

        # Loop, receive and print data with sender context.
        while True:
            data, (host, port, flowinfo, scopeid) = await sock.recvfrom(4096)
            # For consistant output among python versions:
            try: host, interface = host.split('%')
            except ValueError:
                # Python >= 3.7 does not include interface name concatenated
                # to the host portion of the ipv6 addr tuple. so if we want it
                # we must look it up with the numeric scopeid.
                interface = socket.if_indextoname(scopeid)

            print("({}) {} {} -> {}".format(interface, host, port, data.decode()))

    else: # IPv4
        # Join group
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Loop, printing any data we receive and where it came from.
        while True:
            data, (host, port) = await sock.recvfrom(4096)
            print("{} {} -> {}".format(host, str(port), data.decode()))

if __name__ == '__main__':
    group = MYGROUP_6 if "-6" in sys.argv[1:] else MYGROUP_4
    try:
        curio.run(main, group)
    except KeyboardInterrupt:
        curio.run(close, socks)

