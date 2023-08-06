#!/usr/bin/env python

from __future__ import print_function, unicode_literals

from destruct.protocols.netflow import FlowPacket
import socket
import warnings

FMT = "{0.srcaddr:15s} \u2192 {0.dstaddr:15s} : {0.doctets:d} octet(s)"

def listener(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))

    while True:
        data, src_addr = sock.recvfrom(65536)
        try:
            packet = FlowPacket(data)
        except Exception as e:
            warnings.warn("Exception: {!r}".format(e), RuntimeWarning)
            continue

        for record in packet.records:
            print(FMT.format(record))

if __name__ == "__main__":
    print("Listening for packets on 127.0.0.1:3000")
    listener("127.0.0.1", 3000)
