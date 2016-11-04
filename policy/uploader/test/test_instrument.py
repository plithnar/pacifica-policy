#!/usr/bin/python
"""Test the instrument query for the uploader policy."""
from os import getenv
from unittest import TestCase
from json import dumps, loads
import httpretty
from policy.uploader.instrument import InstrumentQuery
from policy.uploader.test.test_base import BaseTestData
from policy import METADATA_ENDPOINT

ADMIN_GROUP = getenv('ADMIN_GROUP', 'admin')


# pylint: disable=too-many-public-methods
class TestInstrumentQuery(TestCase, BaseTestData):
    """Test the instrument query system."""

    prop_participant_json = [
        {'proposal_id': 4, 'person_id': BaseTestData.sample_user_id}
    ]
    prop_instrument_json = [
        {'proposal_id': 4, 'instrument_id': 121},
        {'proposal_id': 4, 'instrument_id': 131}
    ]
    instruments_json = [
        {'_id': 122},
        {'_id': 133},
        {'_id': 144},
        {'_id': 155},
        {'_id': 166}
    ]
    instruments_url = '{0}/instruments'.format(METADATA_ENDPOINT)
    prop_instrument_url = '{0}/proposal_instrument'.format(METADATA_ENDPOINT)
    prop_participant_url = '{0}/proposal_participant'.format(METADATA_ENDPOINT)

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_instruments_is_admin_prop(self):
        """Test the GET instruments method as an admin with proposal."""
        self.init_admin_urls(self.user_group_json)
        httpretty.register_uri(httpretty.GET, self.prop_instrument_url,
                               body=dumps(self.prop_instrument_json),
                               content_type='application/json')
        instq = InstrumentQuery()
        ret = loads(instq.GET(user_id=self.admin_user_id, proposal_id=1))
        for inst in [121, 131]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_instruments_is_admin_no_prop(self):
        """Test the GET instruments method as an admin with no proposal."""
        self.init_admin_urls(self.user_group_json)
        httpretty.register_uri(httpretty.GET, self.instruments_url,
                               body=dumps(self.instruments_json),
                               content_type='application/json')
        instq = InstrumentQuery()
        ret = loads(instq.GET(user_id=self.admin_user_id))
        for inst in [inst['_id'] for inst in self.instruments_json]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_instruments_not_admin_prop(self):
        """Test the GET instruments method as user with proposal."""
        self.init_admin_urls([])
        httpretty.register_uri(httpretty.GET, self.prop_instrument_url,
                               body=dumps(self.prop_instrument_json),
                               content_type='application/json')

        instq = InstrumentQuery()
        ret = loads(instq.GET(user_id=self.sample_user_id, proposal_id=1))
        for inst in [121, 131]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_instruments_not_admin_no_prop(self):
        """Test the GET instruments method as user with no proposal."""
        self.init_admin_urls([])
        httpretty.register_uri(httpretty.GET, self.prop_participant_url,
                               body=dumps(self.prop_participant_json),
                               content_type='application/json')
        httpretty.register_uri(httpretty.GET, self.prop_instrument_url,
                               body=dumps(self.prop_instrument_json),
                               content_type='application/json')

        instq = InstrumentQuery()
        ret = loads(instq.GET(user_id=self.sample_user_id))
        for inst in [121, 131]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name
