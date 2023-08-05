#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from concurrence import Tasklet
from paste import httpserver

from nagare.publishers.concurrence import socket

class WSGIServer(object):
    def __init__(self, wsgi_application, server_address, listen_backlog=socket.SOMAXCONN):
        self.wsgi_application = wsgi_application
        self.server_address = server_address

        self.sock = socket.socket()
        self.sock.bind(server_address)
        self.sock.listen(listen_backlog)

    def run(self):
        while True:
            conn = self.sock.accept()
            if conn is None:
                break

            Tasklet.new(self.handle_request)(*conn)

    def handle_request(self, conn, src):
        httpserver.WSGIHandler(conn, src, self)
        conn.close()
