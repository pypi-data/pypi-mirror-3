from __future__ import absolute_import

from ..structures import StructField
from ..types.ip import IPv4

class IPv4Field(StructField):
    def __init__(self, cls=IPv4):
        super(IPv4Field, self).__init__("L", conversion=IPv4)
