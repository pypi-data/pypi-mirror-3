#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""The eventlet__ publisher

__ http://wiki.secondlife.com/wiki/Eventlet
"""

from concurrence import dispatch
from concurrence.http import WSGIServer

from nagare import local
from nagare.publishers import common

class Publisher(common.Publisher):
    execution_env = local.TASKLETS

    spec = dict(host='string(default=None)', port='integer(default=None)')

    def serve(self, filename, conf, error):
        """Run the publisher

        In:
          -  ``filename`` -- the path to the configuration file
          - ``conf`` -- the ``ConfigObj`` object, created from the configuration file
          - ``error`` -- the function to call in case of configuration errors
        """
        (host, port, conf) = self._validate_conf(filename, conf, error)

        # The publisher is an events based server so call once the ``on_new_process()`` method
        self.on_new_process()

        dispatch(lambda: self.main(host, port))

    def main(self, host, port):
        WSGIServer(self.urls).serve((host, port))
