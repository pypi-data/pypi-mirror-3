#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Scoring

Scoring instance that process loan propositions
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
import time
import random
import sleipnir.core

__all__ = ['Scoring']

# Project requirements
from sleipnir.transport.connections import ConnectionFactory
from sleipnir.transport.patterns.endpoints import Replier

# local submodule requirements
from routes import SCORING_REQUEST_QUEUE, CONNECTION
from messages import ScoringRequest, ScoringResponse


class Scoring(object):

    @property
    def score(self):
        return random.randint(300, 900)

    @property
    def history(self):
        return random.randint(1, 20)

    def process(self, request, properties):
        # compute result
        result = {
            str(ScoringResponse.SSN): request[str(ScoringRequest.SSN)],
            str(ScoringResponse.CREDIT_SCORE): self.score,
            str(ScoringResponse.HISTORY_LENGTH): self.history,
            }

        # sleep thread for msecs
        time.sleep(result[str(ScoringResponse.CREDIT_SCORE)] / 1000)
        # return loan result
        return (result, {})


if __name__ == '__main__':
    # Import here required modules for back standalone execution
    import sys

    # Verify parameters
    try:

        # create a Request reply pattern
        Replier(
            SCORING_REQUEST_QUEUE,
            None,
            CONNECTION, Scoring()).run()

        # notify how could be out
        sys.stdout.write("Press Ctrl-C to exit...\n")

        # start connection
        connection = ConnectionFactory.get_instance().create(CONNECTION)
        connection.loop.start()

    except KeyboardInterrupt:
        # close connection
        connection.close()
