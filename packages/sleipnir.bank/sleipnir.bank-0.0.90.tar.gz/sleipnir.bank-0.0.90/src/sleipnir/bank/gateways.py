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
import re
import random
import operator
import sleipnir.core

__all__ = ['BankGateway']

# Project requirements
from sleipnir.transport.connections import ConnectionFactory
from sleipnir.transport.patterns.endpoints import EndPoint
from sleipnir.transport.patterns.routers import EndPointRelay
from sleipnir.transport.patterns.aggregators import WrapperAggregate
from sleipnir.transport.patterns.aggregators import Aggregator, Header

# local submodule requirements

APP_ID = "app_id"
MESSAGE_ID = "message_id"
REPLY_TO = "reply_to"
CORRELATION_ID = "correlation_id"

from messages import BankQuoteReply


class Loan(object):

    __slots__ = ('_loans', '_nloan')

    # number of banks which propose loans
    expected = 0

    def __init__(self, expected):
        self._loans = []
        self._nloan = expected

    def add_message(self, message):
        self._loans.append(message)

    def is_complete(self, n_loans=None):
        n_loans = n_loans or self._nloan
        return len(self._loans) >= n_loans

    def get_message(self):
        best_loan = {
            str(BankQuoteReply.ERROR_CODE): 1,
            }
        best = 0.0

        for loan in self._loans:
            if loan[str(BankQuoteReply.ERROR_CODE)] == 0:
                interest_rate = loan[str(BankQuoteReply.INTEREST_RATE)]
                if best < interest_rate:
                    best, best_loan = interest_rate, loan
        return best_loan


class BankAggregate(WrapperAggregate):
    __slots__ = ()
    wrapper = Loan


class BankAggregator(EndPoint):

    producer = None

    def __init__(self, callback, request, error, connection=None):
        self._aggregator = Aggregator(
            Header(APP_ID),
            callback,
            BankAggregate)
        super(BankAggregator, self).__init__(request, None, error, connection)
        self._consumer.append_callbacks(self._aggregator.process)

    def __iter__(self):
        return iter(self._aggregator)

    def __getattr__(self, value):
        return getattr(self._aggregator, value)


class BankRelay(EndPointRelay):

    def get_eligible_banks(self, request):
        def parse(value):
            try:
                opr, value = re.match("([<>!=]{1,2})(.*)", str(value)).groups()
                value = int(value)
                # process
                return {
                    '>=': lambda x: operator.ge(x, value),
                    '=>': lambda x: operator.ge(x, value),
                    '=<': lambda x: operator.le(x, value),
                    '<=': lambda x: operator.le(x, value),
                    '<>': lambda x: operator.ne(x, value),
                    '==': lambda x: operator.eq(x, value),
                    '!=': lambda x: operator.ne(x, value),
                    '<':  lambda x: operator.lt(x, value),
                    '>':  lambda x: operator.gt(x, value),
                    }.get(opr, lambda x: False)
            except:
                return lambda x: False

        eligible = self._relay.keys()
        for bank, rules in self._relay.iteritems():
            rules = rules[0].iteritems()
            conditions = [(str(key), parse(val),) for key, val in rules]
            for key, func in conditions:
                if key not in request or not func(int(request[key])):
                    eligible.remove(bank)
                    break
        return eligible


class BankGw(object):

    class BankProcess(object):
        def __init__(self, callback, apply_id):
            self.callback = callback
            self.apply_id = apply_id

    def __init__(self, request, response, control, error, connection=None):
        self._apply_id = 0
        self._processes = {}
        self._response = BankAggregator(
            self._on_response, response, error, connection)
        self._rrequest = BankRelay(request, control, error, connection)

    def _on_response(self, response, message):
        if message:
            process = self._processes.pop(message.properties[APP_ID])
        else:
            # this is a hack to get bank gateway working when no
            # bank is present
            processes = self._processes.keys()
            [processes.remove(key) for key, _ in iter(self._response)]
            process = self._processes.pop(processes[0])
            assert len(processes) == 1
        process.callback(response, message)

    def manage_groups(self, name, banks):
        self._rrequest.route(name, banks)

    def best_quote(self, message, callback):
        banks = self._rrequest.get_eligible_banks(message)
        headers = {
            REPLY_TO: '@' + str(self._response.nodes.consumer.queues[0]),
            APP_ID:   str(random.randint(0, 10000000)),
            }

        # create a process and publish
        process = self.BankProcess(callback, headers[APP_ID])
        self._processes.setdefault(process.apply_id, process)
        self._rrequest.replay(message, headers, banks)

        # set completion value for aggregato
        aggregate = self._response.create(headers[APP_ID], len(banks))
        # enforces a response if no bank is online
        self._response.check(aggregate)

    def run(self, timeout=None):
        self._rrequest.run(timeout)
        self._response.run(timeout)


class ScoringGw(EndPoint):

    class ScoringProcess(object):
        def __init__(self, callback, apply_id):
            self.callback = callback
            self.apply_id = apply_id

    def __init__(self, request, response, error, connection=None):
        self._processes = {}
        super(ScoringGw, self).__init__(request, response, error, connection)
        self._consumer.append_callbacks(self.when_scoring_received)

    def get_scoring(self, request, callback):
        properties = {
            MESSAGE_ID: str(random.randint(0, 10000000)),
            REPLY_TO: self._consumer.queues[0],
            }
        # create a process
        process = self.ScoringProcess(callback, properties[MESSAGE_ID])
        self._processes.setdefault(process.apply_id, process)
        # prepare message and send
        message = self._producer.prepare(request, **properties)
        self._producer.publish(message)

    def when_scoring_received(self, response, message):
        correlation_id = message.properties[CORRELATION_ID]
        if correlation_id in self._processes:
            process = self._processes.pop(correlation_id)
            process.callback(response)
        else:
            # Send message to error queue
            raise NotImplementedError
