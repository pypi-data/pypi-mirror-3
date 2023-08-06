from __future__ import absolute_import

from ..structures import StructBase
from ..fields import U8Field, U16Field, U32Field, TimestampField
from ..fields.ip import IPv4Field
import math

class Flow5Record(StructBase):
    """
    NetFlow version 5 flow record.
    """
    srcaddr   = IPv4Field()
    dstaddr   = IPv4Field()
    nexthop   = IPv4Field()
    input     = U16Field()
    output    = U16Field()
    dpkts     = U32Field()
    doctets   = U32Field()
    first     = TimestampField()
    last      = TimestampField()
    srcport   = U16Field()
    dstport   = U16Field()
    _pad1     = U8Field()
    tcp_flags = U8Field()
    prot      = U8Field()
    tos       = U8Field()
    src_as    = U16Field()
    dst_as    = U16Field()
    src_mask  = U8Field()
    dst_mask  = U8Field()
    _pad2     = U16Field()

class Flow5Packet(StructBase):
    """
    NetFlow version 5 flow packet.
    """
    version           = U16Field()
    count             = U16Field()
    sys_uptime        = U32Field()
    unix_secs         = TimestampField()
    unix_nsecs        = U32Field()
    flow_sequence     = U32Field()
    engine_type       = U8Field()
    engine_id         = U8Field()
    sampling_interval = U16Field()
    # Followed by self.count Flow5Record elements

    def __init__(self, raw_packet):
        packet_len = len(raw_packet)
        record_len = Flow5Record.struct.size
        hdr_len = self.struct.size

        super(Flow5Packet, self).__init__(raw_packet)
        assert self.version == 5

        # If packet's truncated, recalculate count
        if packet_len < self.struct.size + self.count * record_len:
            self.count = int(math.floor((packet_len - hdr_len) / record_len))

        # Extract records
        self.records = []
        for idx in xrange(0, self.count):
            record = Flow5Record(raw_packet[hdr_len + idx * record_len:])
            self.records.append(record)

FlowPacket = Flow5Packet
