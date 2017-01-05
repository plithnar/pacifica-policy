#!/usr/bin/python
"""The CherryPy rest object for the structure."""
# from policy.uploader.instrument import InstrumentQuery
from policy.status.proposal_query import ProposalQuery
from policy.status.instrument_query import InstrumentQuery
from policy.status.transaction_query import TransactionQuery
from policy.status.user_query import UserQuery


# pylint: disable=too-few-public-methods
class StatusPolicy(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed.

    """

    exposed = False

    def __init__(self):
        """Create local objects to allow for import to work."""
        self.instrument = InstrumentQuery()
        self.proposals = ProposalQuery()
        self.transactions = TransactionQuery()
        self.users = UserQuery()
# pylint: enable=too-few-public-methods
