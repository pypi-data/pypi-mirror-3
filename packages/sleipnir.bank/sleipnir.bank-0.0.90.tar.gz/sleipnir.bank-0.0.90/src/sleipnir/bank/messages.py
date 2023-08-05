#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Enums

Common structs used by bank solution
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
import sleipnir.core

__all__ = [
    "BankQuoteReply",
    "BankQuoteRequest",
    "LoanQuoteReply",
    "LoanQuoteRequest",
    "ScoringRequest",
    "ScoringResponse",
    ]


class BankQuoteRequest(enum):
    SSN,            \
    CREDIT_SCORE,   \
    HISTORY_LENGTH, \
    LOAN_TERM,      \
    LOAN_AMOUNT = xrange(0, 5)


class BankQuoteReply(enum):
    INTEREST_RATE,  \
    QUOTE_ID,       \
    ERROR_CODE = xrange(0, 3)


class CreditBureauReply(enum):
    SSN, = xrange(0, 1)


class LoanQuoteRequest(enum):
    SSN,       \
    LOAN_TERM, \
    LOAN_AMOUNT = xrange(0, 3)


class LoanQuoteReply(enum):
    SSN,         \
    QUOTE_ID,    \
    LOAN_AMOUNT, \
    INTEREST_RATE = xrange(0, 4)


class ScoringRequest(enum):
    SSN, = xrange(0, 1)


class ScoringResponse(enum):
    SSN,          \
    CREDIT_SCORE, \
    HISTORY_LENGTH = xrange(0, 3)
