# encoding: utf-8
"""
Helper module for example applications. Mimics ZeroMQ Guide's zhelpers.h.
"""

import binascii
import os
from random import randint

import zmq

# fix ROUTER/DEALER aliases, missing from pyzmq < 2.1.9
if not hasattr(zmq, 'ROUTER'):
    zmq.ROUTER = zmq.XREP
if not hasattr(zmq, 'DEALER'):
    zmq.DEALER = zmq.XREQ


def dump(msg_or_socket):
    "Receives all message parts from socket, prints neatly"
    if isinstance(msg_or_socket, zmq.Socket):
        # it's a socket, call on current message
        return dump(msg_or_socket.recv_multipart())
    else:
        msg = msg_or_socket

    s = "----------------------------------------\n"
    for part in msg:
        s += "[%03d]\n" % len(part)
        is_text = True
        for c in part:
            if ord(c) < 32 or ord(c) > 128:
                is_text = False
                break
        if is_text:
            # print only if ascii text
            s += "%s\n" % part
        else:
            # not text, print hex
            s += "%s\n" % binascii.hexlify(part)
    return s


def set_id(zsocket):
    "Set simple random printable identity on socket"
    identity = "%04x-%04x" % (randint(0, 0x10000), randint(0, 0x10000))
    zsocket.setsockopt(zmq.IDENTITY, identity)


def zpipe(ctx):
    """build inproc pipe for talking to threads
    
    mimic pipe used in czmq zthread_fork.
    
    Returns a pair of PAIRs connected via inproc
    """
    a = ctx.socket(zmq.PAIR)
    a.linger = 0
    b = ctx.socket(zmq.PAIR)
    b.linger = 0
    a.hwm = 1
    b.hwm = 1
    iface = "inproc://%s" % binascii.hexlify(os.urandom(8))
    a.bind(iface)
    b.connect(iface)
    return a,b
    
