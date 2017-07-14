#!/usr/bin/python
"""Base class module for standard queries for the upload status tool."""
import requests
from policy import METADATA_ENDPOINT
from policy.admin import AdminPolicy


# pylint: disable=too-few-public-methods
class QueryBase(AdminPolicy):
    """This pulls the common bits of instrument and proposal query into a single class."""

    all_instruments_url = '{0}/instruments'.format(METADATA_ENDPOINT)
    all_proposals_url = '{0}/proposals'.format(METADATA_ENDPOINT)
    all_transactions_url = '{0}/transactions'.format(METADATA_ENDPOINT)

    prop_participant_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)
    prop_instrument_url = '{0}/proposal_instrument'.format(METADATA_ENDPOINT)

    @staticmethod
    def _get_available_proposals(user_id):
        md_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)
        params = {
            'person_id': user_id
        }
        response = requests.get(url=md_url, params=params)

        return [x.get('proposal_id') for x in response.json()]
# pylint: enable=too-few-public-methods
