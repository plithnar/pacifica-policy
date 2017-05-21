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

    all_users_url = '{0}/users'.format(METADATA_ENDPOINT)
    all_instruments_url = '{0}/instruments'.format(METADATA_ENDPOINT)
    all_proposals_url = '{0}/proposals'.format(METADATA_ENDPOINT)
    prop_participant_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)
    prop_instrument_url = '{0}/proposal_instrument'.format(METADATA_ENDPOINT)

    def __init__(self):
        """Constructor for Uploader Policy."""
        self.admin_group = getenv('ADMIN_GROUP', 'admin')
        self._set_admin_id()

    def _proposals_for_user(self, user_id):
        if self._is_admin(user_id):
            return [prop['_id'] for prop in loads(requests.get(self.all_proposals_url).text)]
        prop_url = '{0}?person_id={1}'.format(self.prop_participant_url, user_id)
        return [part['proposal_id'] for part in loads(requests.get(prop_url).text)]

    def _proposals_for_user_inst(self, user_id, inst_id):
        props = set(self._proposals_for_user(user_id))
        inst_props_url = '{0}?instrument_id={1}'.format(self.prop_instrument_url, inst_id)
        inst_props = loads(requests.get(inst_props_url).text)
        inst_props = set([part['proposal_id'] for part in inst_props])
        return list(props & inst_props)

    def _proposal_info_from_ids(self, prop_list):
        ret = []
        if prop_list:
            for prop_id in prop_list:
                prop_url = '{0}?_id={1}'.format(self.all_proposals_url, prop_id)
                ret.append(loads(requests.get(prop_url).text)[0])
        return ret

    def _instruments_for_user_prop(self, user_id, prop_id):
        ret = []
        if prop_id not in self._proposals_for_user(user_id):
            return ret
        prop_insts_url = '{0}?proposal_id={1}'.format(self.prop_instrument_url, prop_id)
        prop_insts = loads(requests.get(prop_insts_url).text)
        return set([part['instrument_id'] for part in prop_insts])

    def _instrument_info_from_ids(self, inst_list):
        ret = []
        for inst_id in inst_list:
            inst_url = '{0}?_id={1}'.format(self.all_instruments_url, inst_id)
            ret.append(loads(requests.get(inst_url).text)[0])
        return ret

    def _users_for_prop(self, prop_id):
        user_prop_url = '{0}?proposal_id={1}'.format(self.prop_participant_url, prop_id)
        user_props = loads(requests.get(user_prop_url).text)
        return set([part['person_id'] for part in user_props])

    def _user_info_from_kwds(self, **kwds):
        query_list = ['{0}={1}'.format(key, value) for key, value in kwds.items()]
        query_str = '&'.join(query_list)
        user_url = '{0}?{1}'.format(self.all_users_url, query_str)
        return loads(requests.get(user_url).text)

    def _set_admin_id(self):
        agid_query = '{0}/groups?group_name={1}'.format(
            METADATA_ENDPOINT,
            self.admin_group
        )
        admin_group_id = requests.get(agid_query)
        admin_groups = loads(admin_group_id.text)
        if admin_groups:
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
