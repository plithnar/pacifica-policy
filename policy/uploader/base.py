#!/usr/bin/python
"""
Base class module for instrument and proposal queries
"""
from os import getenv
from json import loads
import requests
from policy import METADATA_ENDPOINT

ADMIN_GROUP = getenv('ADMIN_GROUP', 'admin')

# pylint: disable=too-few-public-methods
class QueryBase(object):
    """
    This pulls the common bits of instrument and proposal query into a single
    class
    """

    all_instruments_url = "%s/instruments"%(METADATA_ENDPOINT)
    all_proposals_url = "%s/proposals"%(METADATA_ENDPOINT)
    prop_participant_url = "%s/proposal_participant"%(METADATA_ENDPOINT)
    prop_instrument_url = "%s/proposal_instrument"%(METADATA_ENDPOINT)

    def __init__(self):
        """
        pull the gid for the admin group in the environment
        """
        agid_query = "%s/groups?group_name=%s"%(
            METADATA_ENDPOINT,
            ADMIN_GROUP
        )
        admin_group_id = requests.get(agid_query)
        admin_groups = loads(admin_group_id.text)
        self.admin_group_id = admin_groups[0]['_id']

    def _is_admin(self, user_id):
        """
        Do the query to determine if the user is an admin
        """
        amember_query = "%s/user_group?group_id=%s&person_id=%s"%(
            METADATA_ENDPOINT,
            self.admin_group_id,
            user_id
        )
        is_admin_req = requests.get(amember_query)
        is_admin_list = loads(is_admin_req.text)
        return len(is_admin_list) > 0
# pylint: enable=too-few-public-methods
