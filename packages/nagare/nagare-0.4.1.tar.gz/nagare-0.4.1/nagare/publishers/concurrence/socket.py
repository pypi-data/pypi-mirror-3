#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

import _socket
import string
import sys

from _socket import getaddrinfo, error
from _socket import AF_UNSPEC, SOCK_STREAM, AI_PASSIVE, SOMAXCONN

me = sys.modules[__name__]
for (name, v) in _socket.__dict__.iteritems():
    #if name.startswith(tuple(string.ascii_uppercase)):
    if not name.startswith('_'):
        setattr(me, name, v)

# ---------------------------------------------------------------------------------------------------------------------

from concurrence import io

from nagare.publishers.concurrence import buffered

class socket(object):
    def __init__(self, family=_socket.AF_INET, type=_socket.SOCK_STREAM, proto=0, stream=None):
        self.stream = stream if stream else io.socket.Socket(_socket.socket(family, type, proto))
        self.buffer = buffered.BufferedStream(self.stream)

    def connect(self, addr):
        self.stream._connect(addr)
        #print "Connection", addr, self

    def send(self, data):
        #print "Send", self, data
        self.buffer.writer.write_bytes(data)
        self.buffer.writer.flush()
        return len(data)

    def recv(self, len, *args):
        r = self.buffer.reader.toto(len)
        #print "Recv", self, r
        return r

    def bind(self, *args, **kw):
        return self.stream.bind(*args, **kw)

    def listen(self, *args, **kw):
        return self.stream.listen(*args, **kw)

    def accept(self, *args, **kw):
        return socket(stream=self.stream.accept(*args, **kw)), ('', '')

    def close(self, *args, **kw):
        #print "close", self
        return self.stream.close(*args, **kw)

    def makefile(self, *args, **kw):
        return self.buffer.file()

    def settimeout(self, *args, **kw):
        pass
