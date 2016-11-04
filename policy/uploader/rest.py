#!/usr/bin/python
"""The CherryPy rest object for the structure."""
from policy.uploader.instrument import InstrumentQuery
from policy.uploader.proposal import ProposalQuery


# pylint: disable=too-few-public-methods
class UploaderPolicy(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = False

    def __init__(self):
        """Create local objects to allow for import to work."""
        self.instrument = InstrumentQuery()
        self.proposal = ProposalQuery()
# pylint: enable=too-few-public-methods
