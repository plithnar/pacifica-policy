#!/usr/bin/python
"""CherryPy Status Policy object class."""
from policy.status.transaction.search import TransactionSearch
from policy.status.transaction.lookup import TransactionLookup
from policy.status.transaction.files import FileLookup


# pylint: disable=too-few-public-methods
class TransactionQuery(object):
    """CherryPy root object class."""

    exposed = False

    def __init__(self):
        """Create local objects for sub tree items."""
        self.search = TransactionSearch()
        self.by_id = TransactionLookup()
        self.files = FileLookup()
# pylint: enable=too-few-public-methods
