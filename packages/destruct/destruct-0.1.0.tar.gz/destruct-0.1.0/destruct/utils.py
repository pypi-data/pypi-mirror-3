from __future__ import absolute_import

import time
import socket
import struct

def unix_to_iso(unix_secs):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(unix_secs))

def long_to_ipv4(ip_numeric):
    return socket.inet_ntoa(struct.pack("!L", ip_numeric))

def ipv4_to_long(ip_string):
    return struct.unpack("!L", socket.inet_aton(ip_string))[0]
