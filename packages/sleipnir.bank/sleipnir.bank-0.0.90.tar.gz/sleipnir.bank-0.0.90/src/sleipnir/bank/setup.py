#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Setup

Setup routes
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
import pika.log

# Project requirements
from sleipnir.transport.builder import Builder
from sleipnir.transport.channels import Producer
from sleipnir.transport.connections import ConnectionFactory

# local submodule requirements
import routes


class BankBuilder(Builder):
    # Number of routes already builded
    builded = 0

    def when_resumed(self, route, frame):
        self.builded += 1
        if len(routes.Routes) == self.builded:
            print "routes established. Closing now..."
            self._connection.close()
            self._connection.loop.start()

if __name__ == '__main__':
    # set level error
    pika.log.setup(level=pika.log.INFO)

    # create a connection
    connect = ConnectionFactory.get_instance().create(routes.CONNECTION)
    # create a builder and routes
    builder = connect.routes(BankBuilder, force=True)
    [builder(route) for route in routes.Routes]

    # create now!
    connect.loop.start()
