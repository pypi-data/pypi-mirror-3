from __future__ import absolute_import

from ..utils import long_to_ipv4, ipv4_to_long

class IPv4(object):
    def __init__(self, value):
        if type(value) in (int, long):
            self.value = value
        elif type(value) in (str, unicode):
            self.value = ipv4_to_long(value)
        else:
            raise TypeError("Cannot create IPv4 from {}".format(type(value).__class__.__name__))

    def __str__(self):
        return long_to_ipv4(self.value)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, str(self))

class IPv4Network(IPv4):
    def __init__(self, cidr):
        if "/" not in cidr:
            raise ValueError("IPv4Network must be initialized from a CIDR block string")
        ip, self.bits = cidr.split("/", 1)
        self.bitmask = (0xffffffff << (32-int(self.bits))) & 0xffffffff
        super(IPv4Network, self).__init__(ip)
        self.value &= self.bitmask

    def __str__(self):
        return "{}/{:d}".format(super(IPv4Network, self).__str__(), self.bits)

    def __contains__(self, address):
        if hasattr(address, "value"):
            value = address.value
        else:
            value = address
        return value & self.bitmask == self.value
