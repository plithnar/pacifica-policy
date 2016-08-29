#!/usr/bin/python
"""
CherryPy Uploader Policy object class
"""
from policy.uploader.instrument import InstrumentQuery
from policy.uploader.proposal import ProposalQuery

# pylint: disable=too-few-public-methods
class UploaderPolicy(object):
    """
    CherryPy root object class

    not exposed by default the base objects are exposed
    """
    exposed = False
    instrument = InstrumentQuery()
    proposal = ProposalQuery()
# pylint: enable=too-few-public-methods
