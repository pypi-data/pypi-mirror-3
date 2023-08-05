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
from random import randint

__all__ = ['LoanBroker']

# Project requirements
from sleipnir.core.decorators import cached
from sleipnir.core.utils import maybe_list, uuid
from sleipnir.transport.channels import ChannelEnd, Producer, Consumer
from sleipnir.transport.connections import ConnectionFactory
from sleipnir.transport.patterns.endpoints import Manager
from sleipnir.transport.patterns.translators import Translator

# local submodule requirements
import routes
from messages import *
from gateways import BankGw, ScoringGw


MESSAGE_ID = 'message_id'
CORRELATION_ID = 'correlation_id'


class LoanBrokerTranslator(Translator):
    def __init__(self):
        super(LoanBrokerTranslator, self).__init__()
        self.register(ScoringRequest, None)
        self.register(BankQuoteRequest, self._template_bank_quote_request)
        self.register(LoanQuoteReply, self._template_loan_quote_reply)

    def _template_bank_quote_request(self, result, klass, *values):
        loan_ssn = values[0][str(LoanQuoteRequest.SSN)]
        cred_ssn = values[1][str(ScoringResponse.SSN)]
        return result if (loan_ssn == cred_ssn) else None

    def _template_loan_quote_reply(self, result, klass, *values):
        if not result[str(LoanQuoteReply.QUOTE_ID)]:
            result[str(LoanQuoteReply.INTEREST_RATE)] = 0.0
            result[str(LoanQuoteReply.QUOTE_ID)] = "ERROR: No Qualifying Quote"
        return result


class LoanBrokerProcess(object):
    def __init__(self, manager, message):
        self._manager = manager
        self._message = message
        self._request = message.payload

    def _when_scoring_replied(self, message):
        translator, request = self._translator, self._request
        brq = translator(BankQuoteRequest).convert(request, message)
        brq and self._manager.banks.best_quote(brq, self._when_banks_replied)

    def _when_banks_replied(self, response, message):
        # prepare response
        props = {
            CORRELATION_ID: self._message.properties[MESSAGE_ID],
            MESSAGE_ID: uuid(),
            }
        translator, request = self._translator, self._request
        response = translator(LoanQuoteReply).convert(request, response)
        # now reply
        self._manager.reply(response, **props)
        self._manager.when_completed(props[CORRELATION_ID])

    def run(self, timeout=None):
        self._translator = translator = LoanBrokerTranslator()
        request = translator(ScoringRequest).convert(self._request)
        self._manager.scoring.get_scoring(request, self._when_scoring_replied)


class LoanBroker(Manager):

    # bank gateway
    bank = BankGw
    bank_opts = {
        'response': routes.BANK_GW_REPLY_QUEUE,
        'control':  routes.BANK_GW_CONTROL_QUEUE,
        'request':  None,
        'error':    None,
    }

    # scoring gateway
    cred = ScoringGw
    cred_opts = {
        'response': routes.SCORING_GW_REQUEST_EXCHANGE,
        'request':  routes.SCORING_GW_REPLY_QUEUE,
        'error':    None,
    }

    def __init__(self, bank=None, cred=None, endpoints=None, connection=None):
        super(LoanBroker, self).__init__(endpoints)
        self._bank = bank or self.bank(connection=connection, **self.bank_opts)
        self._cred = cred or self.cred(connection=connection, **self.cred_opts)

    def run(self, timeout=None):
        # start listening to clients
        self._bank.run(timeout)
        self._cred.run(timeout)
        # now listen to all consumers
        super(LoanBroker, self).run(timeout)

    def process(self, end, request, message):
        message_id = message.properties[MESSAGE_ID]
        lb_process = LoanBrokerProcess(self, message)
        self._processes.setdefault(message_id, lb_process).run()

    def reply(self, response, **properties):
        for producer in self._producers.itervalues():
            message = producer.prepare(response, **properties)
            producer.publish(message)

    def when_completed(self, message_id):
        del self._processes[message_id]

    @property
    def scoring(self):
        return self._cred

    @property
    def banks(self):
        return self._bank

if __name__ == '__main__':
    # Import here required modules for back standalone execution
    import sys

    try:
        # create manager endpoints
        endpoints = [
            ChannelEnd.create(
                routes.LOAN_REQUEST_QUEUE,
                Consumer,
                connection=routes.CONNECTION),
            ChannelEnd.create(
                routes.LOAN_REPLY_EXCHANGE,
                Producer,
                connection=routes.CONNECTION),
            ]
        # create manager and start
        LoanBroker(endpoints=endpoints, connection=routes.CONNECTION).run()

        # notify how could be out
        sys.stdout.write("Press Ctrl-C to exit...\n")

        # start connection
        connection = ConnectionFactory.get_instance().create(routes.CONNECTION)
        connection.loop.start()

    except KeyboardInterrupt:
        # close connection
        connection.close()
