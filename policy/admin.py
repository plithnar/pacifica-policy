#!/usr/bin/python
"""The Admin module has logic about checking for admin group info."""
from os import getenv
from json import loads
import requests
from policy import METADATA_ENDPOINT


# pylint: disable=too-few-public-methods
class AdminPolicy(object):
    """
    Enforces the admin policy.

    Base class for checking for admin group membership or not.
    """

    def __init__(self):
        """Constructor for Uploader Policy."""
        self.admin_group = getenv('ADMIN_GROUP', 'admin')
        self._set_admin_id()

    def _set_admin_id(self):
        agid_query = '{0}/groups?group_name={1}'.format(
            METADATA_ENDPOINT,
            self.admin_group
        )
        admin_group_id = requests.get(agid_query)
        admin_groups = loads(admin_group_id.text)
        if len(admin_groups):
            self.admin_group_id = admin_groups[0]['_id']
        else:
            self.admin_group_id = -1

    def _is_admin(self, user_id):
        if self.admin_group_id == -1:
            self._set_admin_id()
        amember_query = '{0}/user_group?group_id={1}&person_id={2}'.format(
            METADATA_ENDPOINT,
            self.admin_group_id,
            user_id
        )
        is_admin_req = requests.get(amember_query)
        is_admin_list = loads(is_admin_req.text)
        return len(is_admin_list) > 0
# pylint: enable=too-few-public-methods
