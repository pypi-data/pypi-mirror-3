#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Client

Client instance that process loan propositions
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
import functools
import sleipnir.core

from random import randint
from time import sleep, time
from pprint import pprint

__all__ = ['Client']

# Project requirements
from sleipnir.core.utils import uuid
from sleipnir.transport.connections import ConnectionFactory
from sleipnir.transport.patterns.endpoints import Requestor

# local submodule requirements
from routes import CLIENT_REQUEST_EXCHANGE, CLIENT_REPLY_QUEUE, CONNECTION
from messages import LoanQuoteRequest

MESSAGE_ID = 'message_id'
CORRELATION_ID = 'correlation_id'
TIMESTAMP = 'timestamp'


class Client(object):
    def __init__(self, nmessages=100):
        self._num_messages = int(nmessages)
        self._buf_messages = {}

    def prepared(self, message):
        return message

    def request(self, message=None, properties={}):
        for count in xrange(0, self._num_messages):
            request = {
                str(LoanQuoteRequest.SSN): count,
                str(LoanQuoteRequest.LOAN_TERM): randint(0, 72) + 12,
                str(LoanQuoteRequest.LOAN_AMOUNT): randint(0, 20) * 5000 + 25000,
                }
            properties = {
                MESSAGE_ID: uuid(),
                TIMESTAMP: time(),
                }

            # return created message
            yield self._buf_messages.setdefault(count, (request, properties,))

    def published(self, request, message):
        self._buf_messages[message[3].message_id] = message
        ssn = request[str(LoanQuoteRequest.SSN)]
        sleep(0.100)

    def response(self, response, message):
        messageid = message.properties[CORRELATION_ID]
        timestamp = time() - self._buf_messages[messageid][3].timestamp
        del self._buf_messages[messageid]
        # show response
        print "Received: ", timestamp * 1000, " millisecs"
        pprint(response, indent=4)


if __name__ == '__main__':
    # Import here required modules for back standalone execution
    import sys

    # Verify parameters
    if len(sys.argv) == 2:
        try:
            # Create bank service
            client = Client(*sys.argv[1:])

            # Create a request reply pattern
            Requestor(
                CLIENT_REPLY_QUEUE,
                CLIENT_REQUEST_EXCHANGE,
                None,
                CONNECTION, client).run()

            # notify how could be out
            sys.stdout.write("Press Ctrl-C to exit...\n")

            # start connection
            connection = ConnectionFactory.get_instance().create(CONNECTION)
            connection.loop.start()

        except KeyboardInterrupt:
            # close connection
            connection.close()
    else:
        sys.stderr.write(
            "Usage: " + sys.argv[0] + " <num messages>\n")
