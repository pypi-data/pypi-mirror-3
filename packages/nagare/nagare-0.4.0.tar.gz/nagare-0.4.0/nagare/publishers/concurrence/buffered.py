#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from concurrence.io import buffered

class BufferedReader(buffered.BufferedReader):
    def toto(self, n):
        r = self.buffer.remaining
        if not r:
            try:
                self._read_more()
            except EOFError:
                return 0

            r = self.buffer.remaining

        return self.buffer.read_bytes(min(n, r))


class CompatibleFile(buffered.CompatibleFile):
    closed = False

    def readline(self, max=-1):
        return self.readlines().next()

    def close(self):
        self.closed = True


class BufferedStream(buffered.BufferedStream):
    def __init__(self, stream, buffer_size=1024*8, read_buffer_size=0, write_buffer_size=0):
        super(BufferedStream, self).__init__(stream, buffer_size, read_buffer_size, write_buffer_size)
        self.reader = BufferedReader(stream, self.reader.buffer)

    def file(self):
        return CompatibleFile(self.reader, self.writer)
