#!/usr/bin/python
"""
CherryPy Uploader Policy object class
"""
from json import dumps, loads
from sets import Set
import requests
from policy.uploader.base import QueryBase

# pylint: disable=too-few-public-methods
class ProposalQuery(QueryBase):
    """
    CherryPy root object class

    not exposed by default the base objects are exposed
    """
    exposed = True

    def _get(self, user_id, instrument_id=None):
        """
        Return the list of proposals given the user and
        an optional instrument_id
        """
        if self._is_admin(user_id):
            all_proposals = requests.get(self.all_proposals_url)
            all_proposals = Set([prop['_id'] for prop in loads(all_proposals.text)])
        else:
            all_proposals = "%s?person_id=%s"%(self.prop_participant_url, user_id)
            all_proposals = requests.get(all_proposals)
            all_proposals = Set([item['proposal_id'] for item in loads(all_proposals.text)])
        if instrument_id:
            inst_props = "%s?instrument_id=%s"%(self.prop_instrument_url, instrument_id)
            inst_props = requests.get(inst_props)
            inst_props = Set([item['proposal_id'] for item in loads(inst_props.text)])
            all_proposals = all_proposals.intersection(inst_props)
        return dumps(list(all_proposals))

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    def GET(self, *args, **kwargs):
        """
        CherryPy GET method
        """
        user_id = None
        instrument_id = None
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        if 'instrument_id' in kwargs:
            instrument_id = kwargs['instrument_id']
        if len(args) > 0:
            user_id = args[0]
        if len(args) > 1:
            instrument_id = args[1]
        return self._get(user_id, instrument_id)
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
