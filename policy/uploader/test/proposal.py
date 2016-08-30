#!/usr/bin/python
"""
Test the proposal query for the uploader policy
"""
from os import getenv
from unittest import TestCase
from json import dumps, loads
import httpretty
from policy.uploader.proposal import ProposalQuery
from policy.uploader.test.base import BaseTestData
from policy import METADATA_ENDPOINT

ADMIN_GROUP = getenv('ADMIN_GROUP', 'admin')

# pylint: disable=too-many-public-methods
class TestProposalQuery(TestCase, BaseTestData):
    """
    Test the proposal query system
    """
    prop_participant_json = [
        {"proposal_id": 4, "person_id": BaseTestData.sample_user_id}
    ]
    prop_instrument_json = [
        {"proposal_id": 5, "instrument_id": 121},
        {"proposal_id": 4, "instrument_id": 121}
    ]
    proposals_json = [
        {"_id": 2},
        {"_id": 3},
        {"_id": 4},
        {"_id": 5},
        {"_id": 6}
    ]
    proposals_url = "%s/proposals"%(METADATA_ENDPOINT)
    prop_instrument_url = "%s/proposal_instrument"%(METADATA_ENDPOINT)
    prop_participant_url = "%s/proposal_participant"%(METADATA_ENDPOINT)

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_proposals_is_admin_inst(self):
        """
        Test the GET instruments method as an admin with
        proposal
        """
        self.init_admin_urls(self.user_group_json)
        httpretty.register_uri(httpretty.GET, self.proposals_url,
                               body=dumps(self.proposals_json),
                               content_type="application/json")
        httpretty.register_uri(httpretty.GET, self.prop_instrument_url,
                               body=dumps(self.prop_instrument_json),
                               content_type="application/json")
        instq = ProposalQuery()
        ret = loads(instq.GET(user_id=self.admin_user_id, instrument_id=121))
        self.assertEqual(len(ret), 2)
        for prop in [4, 5]:
            self.assertTrue(prop in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_proposals_is_admin_no_inst(self):
        """
        Test the GET instruments method as an admin with no
        proposal
        """
        self.init_admin_urls(self.user_group_json)
        httpretty.register_uri(httpretty.GET, self.proposals_url,
                               body=dumps(self.proposals_json),
                               content_type="application/json")
        instq = ProposalQuery()
        ret = loads(instq.GET(user_id=self.admin_user_id))
        for prop in [prop['_id'] for prop in self.proposals_json]:
            self.assertTrue(prop in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_proposals_not_admin_inst(self):
        """
        Test the GET instruments method as user with
        proposal
        """
        self.init_admin_urls([])
        httpretty.register_uri(httpretty.GET, self.prop_instrument_url,
                               body=dumps(self.prop_instrument_json),
                               content_type="application/json")
        httpretty.register_uri(httpretty.GET, self.prop_participant_url,
                               body=dumps(self.prop_participant_json),
                               content_type="application/json")

        instq = ProposalQuery()
        ret = loads(instq.GET(user_id=self.sample_user_id, instrument_id=121))
        self.assertEqual(len(ret), 1)
        for inst in [4]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name

    # pylint: disable=invalid-name
    @httpretty.activate
    def test_get_proposals_not_admin_no_inst(self):
        """
        Test the GET instruments method as user with no
        proposal
        """
        self.init_admin_urls([])
        httpretty.register_uri(httpretty.GET, self.prop_participant_url,
                               body=dumps(self.prop_participant_json),
                               content_type="application/json")

        instq = ProposalQuery()
        ret = loads(instq.GET(user_id=self.sample_user_id))
        self.assertEqual(len(ret), 1)
        for inst in [4]:
            self.assertTrue(inst in ret)
    # pylint: enable=invalid-name
