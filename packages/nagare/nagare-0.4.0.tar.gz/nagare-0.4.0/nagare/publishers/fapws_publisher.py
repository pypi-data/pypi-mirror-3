#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""The FAPWS3__  publisher

__ http://william-os4y.livejournal.com/
"""

import fapws.base
import fapws._evwsgi as evwsgi

from nagare.publishers import common

class Publisher(common.Publisher):
    """The FAPWS3 publisher"""

    # Possible command line options with the default values
    # ------------------------------------------------------

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

        evwsgi.start(host, str(port))
        evwsgi.set_base_module(fapws.base)
        evwsgi.wsgi_cb(self.urls)
        evwsgi.run()
