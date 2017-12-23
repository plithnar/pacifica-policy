#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from policy.validation import validate_proposal
from policy.globals import METADATA_ENDPOINT


# pylint: disable=too-few-public-methods
class ProposalLookup(object):
    """Retrieves details of a given proposal."""

    exposed = True

    @staticmethod
    def _get_proposals_details(proposal_id=None):
        """Return a details about this proposal."""
        lookup_url = u'{0}/proposalinfo/by_proposal_id/{1}'.format(
            METADATA_ENDPOINT, proposal_id
        )
        return requests.get(url=lookup_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_proposal()
    def GET(proposal_id=None):
        """CherryPy GET method."""
        return ProposalLookup._get_proposals_details(proposal_id)
# pylint: enable=too-few-public-methods
