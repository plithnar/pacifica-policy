#!/usr/bin/python
"""CherryPy Uploader Policy object class."""
from json import dumps, loads
import requests
from policy.uploader.base import QueryBase


# pylint: disable=too-few-public-methods
class InstrumentQuery(QueryBase):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = True

    def _get(self, user_id, proposal_id=None):
        """
        Return the list of instruments.

        Return list of instruments given the user and an optional proposal_id
        """
        all_proposals = []
        if proposal_id:
            all_proposals.append(proposal_id)
        else:
            if self._is_admin(user_id):
                all_instruments = loads(requests.get(self.all_instruments_url).text)
                all_instruments = set([inst['_id'] for inst in all_instruments])
                return dumps(list(all_instruments))
            else:
                all_proposals_url = '{0}?person_id={1}'.format(self.prop_participant_url, user_id)
                all_proposals = loads(requests.get(all_proposals_url).text)
                all_proposals = [item['proposal_id'] for item in all_proposals]
        all_inst_list = []
        for prop in all_proposals:
            insts_for_prop = '{0}?proposal_id={1}'.format(self.prop_instrument_url, prop)
            insts_for_prop = requests.get(insts_for_prop)
            all_inst_list += [item['instrument_id'] for item in loads(insts_for_prop.text)]
        all_instruments = set(all_inst_list)
        return dumps(list(all_instruments))

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    def GET(self, *args, **kwargs):
        """CherryPy GET method."""
        user_id = None
        proposal_id = None
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        if 'proposal_id' in kwargs:
            proposal_id = kwargs['proposal_id']
        if len(args) > 0:
            user_id = args[0]
        if len(args) > 1:
            proposal_id = args[1]
        return self._get(user_id, proposal_id)
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
