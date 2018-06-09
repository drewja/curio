#!/usr/bin/env python3

"""
Send/receive UDP multicast packets.
Requires that your OS kernel supports IP multicast.

Usage:
  mcast -s (sender, IPv4)
  mcast -s -6 (sender, IPv6)
  mcast    (receivers, IPv4)
  mcast  -6  (receivers, IPv6)
"""

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 2 # Increase or remove to reach other networks

import time
import struct
import socket
import sys

import curio
from curio import socket

async def serve(group):
    addrinfo = (await socket.getaddrinfo(group, None))[0]

    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    
    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', MYTTL)
    if addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)
    
    data = repr(time.time()).encode()
    await s.sendto(data, (addrinfo[4][0], MYPORT))  
    print(s.getsockname())
    while True:
        data = repr(time.time()).encode()
        await s.sendto(data, (addrinfo[4][0], MYPORT))
        await curio.sleep(1.0)


if __name__ == '__main__':
    group = MYGROUP_6 if "-6" in sys.argv[1:] else MYGROUP_4
    curio.run(serve, group)
