#!/usr/bin/python
"""Base class module for instrument and proposal queries."""
from os import getenv
from json import loads
import requests
from policy import METADATA_ENDPOINT

ADMIN_GROUP = getenv('ADMIN_GROUP', 'admin')


# pylint: disable=too-few-public-methods
class QueryBase(object):
    """This pulls the common bits of instrument and proposal query into a single class."""

    all_instruments_url = '{0}/instruments'.format(METADATA_ENDPOINT)
    all_proposals_url = '{0}/proposals'.format(METADATA_ENDPOINT)
    prop_participant_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)
    prop_instrument_url = '{0}/proposal_instrument'.format(METADATA_ENDPOINT)

    def __init__(self):
        """Pull the gid for the admin group in the environment."""
        agid_query = '{0}/groups?group_name={1}'.format(
            METADATA_ENDPOINT,
            ADMIN_GROUP
        )
        admin_group_id = requests.get(agid_query)
        admin_groups = loads(admin_group_id.text)
        if len(admin_groups):
            self.admin_group_id = admin_groups[0]['_id']
        else:
            self.admin_group_id = -1

    def _is_admin(self, user_id):
        """Do the query to determine if the user is an admin."""
        # if we couldn't init properly try again...
        if self.admin_group_id == -1:
            self.__init__()
        amember_query = '{0}/user_group?group_id={1}&person_id={2}'.format(
            METADATA_ENDPOINT,
            self.admin_group_id,
            user_id
        )
        is_admin_req = requests.get(amember_query)
        is_admin_list = loads(is_admin_req.text)
        return len(is_admin_list) > 0
# pylint: enable=too-few-public-methods
