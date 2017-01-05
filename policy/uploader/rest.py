#!/usr/bin/python
"""The CherryPy rest object for the structure."""
from json import loads, dumps
from cherrypy import tools, request, HTTPError
import requests
from policy import METADATA_ENDPOINT
from policy.admin import AdminPolicy


# pylint: disable=too-few-public-methods
class UploaderPolicy(AdminPolicy):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    all_users_url = '{0}/users'.format(METADATA_ENDPOINT)
    all_instruments_url = '{0}/instruments'.format(METADATA_ENDPOINT)
    all_proposals_url = '{0}/proposals'.format(METADATA_ENDPOINT)
    prop_participant_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)
    prop_instrument_url = '{0}/proposal_instrument'.format(METADATA_ENDPOINT)
    exposed = True

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

    @staticmethod
    def _filter_results(results, *args):
        for result in results:
            for key in result.keys():
                if key not in args:
                    del result[key]

    @staticmethod
    def _clean_user_query_id(query):
        """determine the user_id for whatever is in the query."""
        try:
            return int(query['user'])
        except ValueError:
            return None

    # pylint: disable=too-many-branches
    def _query_select(self, query):
        user_id = self._clean_user_query_id(query)
        wants_object = query['from']
        where_objects = query['where'].keys()
        if wants_object == 'users':
            user_queries = []
            if 'network_id' in where_objects:
                user_queries.append({'network_id': query['where']['network_id']})
            elif 'proposal_id' in where_objects:
                for prop_user_id in self._users_for_prop(query['where']['proposal_id']):
                    user_queries.append({'_id': prop_user_id})
            else:
                user_queries.append({'_id': user_id})
            ret = []
            for user_query in user_queries:
                ret.append(self._user_info_from_kwds(**user_query)[0])
            return ret
        if wants_object == 'proposals':
            if 'instrument_id' in where_objects:
                prop_ids = self._proposals_for_user_inst(user_id, query['where']['instrument_id'])
            elif '_id' in query['where']:
                prop_ids = [query['where']['_id']]
            else:
                prop_ids = self._proposals_for_user(user_id)
            return self._proposal_info_from_ids(prop_ids)
        if wants_object == 'instruments':
            if 'proposal_id' in query['where']:
                inst_ids = self._instruments_for_user_prop(user_id, query['where']['proposal_id'])
            elif '_id' in query['where']:
                inst_ids = [query['where']['_id']]
            return self._instrument_info_from_ids(inst_ids)
        raise TypeError('Invalid Query: ' +
                        'Not sure how to want {0} where {1}'.format(wants_object, query['where']))
    # pylint: enable=too-many-branches

    @staticmethod
    def _valid_query(query):
        if 'user' not in query:
            return False
        if 'from' not in query:
            return False
        if 'columns' not in query:
            return False
        return True

    # pylint: disable=invalid-name
    @tools.json_out()
    @tools.json_in()
    def POST(self):
        """Read in the json query and return results."""
        query = request.json
        if not self._valid_query(query):
            raise HTTPError(500, dumps({'message': 'Invalid Query.', 'status': 'error'}))
        results = self._query_select(query)
        self._filter_results(results, *(query['columns']))
        return results
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
