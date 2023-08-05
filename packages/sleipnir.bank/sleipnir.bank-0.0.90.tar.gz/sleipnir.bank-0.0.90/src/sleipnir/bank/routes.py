#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Routes

Routes used by bank solution
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

#transport connection
CONNECTION = "amqp://guest:guest@localhost:5672/"
DEFAULT_EXCHANGE = ""

#client request ends
CLIENT_REQUEST_EXCHANGE = "lb.exchanges.Client"
CLIENT_REPLY_QUEUE = "lb.queues.Client"

#loan reply ends
LOAN_REPLY_EXCHANGE = "lb.exchanges.LoanBroker"
LOAN_REQUEST_QUEUE = "lb.queues.LoanBroker"

# Scoring gw ends
SCORING_GW_REQUEST_EXCHANGE = "lb.exchanges.ScoringGw"
SCORING_GW_REPLY_QUEUE = "lb.queues.ScoringGw"

#scoring ends
SCORING_REQUEST_QUEUE = "lb.queues.Scoring"

# Bank ends
BANK_GW_REPLY_QUEUE = "lb.queues.bankReply"
BANK_GW_CONTROL_QUEUE = "lb.control.bankGroups"
BANK_GW_CONTROL_EXCHANGE = "lb.control.bankGroups"

Routes = [
    # client loan relationships
    "direct://%s/%s" % (CLIENT_REQUEST_EXCHANGE, LOAN_REQUEST_QUEUE,),
    "direct://%s/%s" % (LOAN_REPLY_EXCHANGE, CLIENT_REPLY_QUEUE,),

    # loan scoring relationships
    "direct://%s/%s" % (SCORING_GW_REQUEST_EXCHANGE, SCORING_REQUEST_QUEUE,),
    "direct://%s/%s" % (DEFAULT_EXCHANGE, SCORING_GW_REPLY_QUEUE,),

    # Bank relationships
    "direct://%s/%s" % (BANK_GW_CONTROL_EXCHANGE, BANK_GW_CONTROL_QUEUE,),
    "direct://%s/%s" % (DEFAULT_EXCHANGE, BANK_GW_REPLY_QUEUE,),
]
