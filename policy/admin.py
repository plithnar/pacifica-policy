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
    inst_custodian_url = '{0}/instrument_custodian'.format(METADATA_ENDPOINT)

    def __init__(self):
        """Constructor for Uploader Policy."""
        self.admin_group = getenv('ADMIN_GROUP', 'admin')
        self._set_admin_id()

    def _proposals_for_user(self, user_id):
        if self._is_admin(user_id):
            return [prop['_id'] for prop in loads(requests.get(self.all_proposals_url).text)]

        prop_url = '{0}?person_id={1}'.format(self.prop_participant_url, user_id)
        return [part['proposal_id'] for part in loads(requests.get(prop_url).text)]

    def _proposals_for_custodian(self, user_id):
        inst_list = self._instruments_for_custodian(user_id)
        proposals_for_custodian = set([])
        for inst in inst_list:
            proposals = self._proposals_for_inst(inst)
            proposals_for_custodian = proposals_for_custodian.union(proposals)
        return list(proposals_for_custodian)

    def _instruments_for_custodian(self, user_id):
        inst_custodian_associations_url = '{0}?custodian_id={1}'.format(
            self.inst_custodian_url, user_id)
        inst_custodian_list = loads(requests.get(inst_custodian_associations_url).text)
        return [i['instrument_id'] for i in inst_custodian_list]

    def _proposals_for_inst(self, inst_id):
        inst_props_url = '{0}?instrument_id={1}'.format(self.prop_instrument_url, inst_id)
        inst_props = loads(requests.get(inst_props_url).text)
        inst_props = set([part['proposal_id'] for part in inst_props])
        return inst_props

    # This should be included once we get the concepts of instrument group
    # pylint: disable=unused-argument
    def _proposals_for_user_inst(self, user_id, inst_id):
        props = set(self._proposals_for_user(user_id))
        if self._is_admin(user_id):
            return props
        props_for_custodian = self._proposals_for_custodian(user_id)
        return list(props.union(props_for_custodian))
    # pylint: enable=unused-argument

    def _proposal_info_from_ids(self, prop_list):
        ret = []
        if prop_list:
            for prop_id in prop_list:
                prop_url = u'{0}?_id={1}'.format(self.all_proposals_url, prop_id)
                ret.append(loads(requests.get(prop_url).text)[0])
        return ret

    def _instruments_for_user(self, user_id):
        if self._is_admin(user_id):
            return [inst['_id'] for inst in loads(requests.get(self.all_instruments_url).text)]
        return self._instruments_for_custodian(user_id)

    def _instruments_for_user_prop(self, user_id, prop_id):
        user_insts = set(self._instruments_for_user(user_id))
        prop_insts = set()
        if prop_id in self._proposals_for_user(user_id):
            prop_insts_url = u'{0}?proposal_id={1}'.format(self.prop_instrument_url, prop_id)
            prop_insts = set([part['instrument_id'] for part in loads(requests.get(prop_insts_url).text)])
        return list(prop_insts | user_insts)

    def _instrument_info_from_ids(self, inst_list):
        ret = []
        for inst_id in inst_list:
            inst_url = '{0}?_id={1}'.format(self.all_instruments_url, inst_id)
            ret.append(loads(requests.get(inst_url).text)[0])
        return ret

    def _users_for_prop(self, prop_id):
        user_prop_url = u'{0}?proposal_id={1}'.format(self.prop_participant_url, prop_id)
        user_props = loads(requests.get(user_prop_url).text)
        return list(set([str(part['person_id']) for part in user_props]))

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

    @staticmethod
    def _object_id_valid(object_lookup_name, object_id):
        if not object_id:
            return False
        object_type_url = '{0}/{1}'.format(METADATA_ENDPOINT, object_lookup_name)
        object_query_url = u'{0}?_id={1}'.format(object_type_url, object_id)
        object_value_req = requests.get(object_query_url)
        object_is_valid = loads(object_value_req.text)
        return len(object_is_valid) > 0

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
