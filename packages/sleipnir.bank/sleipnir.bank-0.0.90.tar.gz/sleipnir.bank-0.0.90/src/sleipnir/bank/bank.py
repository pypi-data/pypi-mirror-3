#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Bank

Bank instance that process loan propositions
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
import random
import sleipnir.core

__all__ = ['Bank']

APP_ID = 'app_id'

# Project requirements
from sleipnir.transport.patterns.endpoints import Replier

from sleipnir.transport.connections import ConnectionFactory
from sleipnir.transport.channels import Producer
from sleipnir.transport.builder import Builder
from sleipnir.transport.enums import ChannelTargetState

# local submodule requirements
from routes import SCORING_REQUEST_QUEUE, BANK_GW_CONTROL_EXCHANGE
from routes import DEFAULT_EXCHANGE, CONNECTION
from messages import BankQuoteReply, BankQuoteRequest


class BankControl(Producer):
    def __init__(self, exchange, connection, bank):
        super(BankControl, self).__init__(exchange, connection)
        self.bank = bank

    def when_resumed(self, route, frame):
        limits, exchange = self.bank.limits, self.bank.queue
        self.publish(self.prepare(limits, reply_to="@" + exchange))

    def when_suspended(self, route, frame):
        self.publish(self.prepare(None, reply_to=self.bank.queue))


class Bank(object):

    # Banks rate
    rate_premium = 0.0

    def __init__(self, name, rate, maxloan, *args):
        self.name = name
        self.rate = float(rate)
        self.loan = int(maxloan)
        self.args = args
        # quote counter
        self.__counter = 0

    @property
    def limits(self):
        return {
            str(BankQuoteRequest.LOAN_AMOUNT): self.args[2],
            str(BankQuoteRequest.CREDIT_SCORE): self.args[0],
            str(BankQuoteRequest.HISTORY_LENGTH): self.args[1],
            }

    def iterest_rate(self, loanterm):
        if  loanterm > self.loan:
            return 0.0
        lterm = (loanterm / 12) / 10
        return self.rate + self.rate_premium + lterm + random.uniform(0, 1)

    def quote_id(self):
        qid = "%s-%0*d" % (self.name, 10, self.__counter)
        self.__counter += 1
        return qid

    def process(self, request, properties):
        tae = self.iterest_rate(request[str(BankQuoteRequest.LOAN_TERM)])
        # prepare result
        result = {
            str(BankQuoteReply.QUOTE_ID): self.quote_id(),
            str(BankQuoteReply.ERROR_CODE): 1 if not tae else 0,
            str(BankQuoteReply.INTEREST_RATE): tae,
            }
        # increment counter and return
        return (result, {APP_ID: properties[APP_ID]})


if __name__ == '__main__':
    # Import here required modules for back standalone execution
    import sys

    # Verify parameters
    if len(sys.argv) == 7:
        try:
            # Create bank service
            bank = Bank(*sys.argv[1:])
            bank.queue = "lb.queues." + bank.name

            # Setup control messages
            control = BankControl(BANK_GW_CONTROL_EXCHANGE, CONNECTION, bank)
            control.watch(state=ChannelTargetState.RESUMED, first=True)
            #FIXME: We can only add an state watch
            #control.watch(state=ChannelTargetState.SUSPENDED, first=True)

            # create a Request reply pattern
            replier = Replier(bank.queue, None, CONNECTION, bank)
            # wait till builder set up queu
            replier.nodes.consumer.watch(first=True)
            replier.run()

            # create route builder
            connection = ConnectionFactory.get_instance().create(CONNECTION)
            builder = connection.routes(Builder, force=True)
            builder("direct://%s/%s" % (DEFAULT_EXCHANGE, bank.queue))

            # notify how could be out
            sys.stdout.write("Press Ctrl-C to exit...\n")
            connection.loop.start()

        except KeyboardInterrupt:
            # close connection
            connection.close()
            connection.loop.start()
    else:
        sys.stderr.write(
            "Usage: " + sys.argv[0] + \
            " <name> <rate> <maxloan> <scoring>, <history> <amount>\n")
