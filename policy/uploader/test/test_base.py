#!/usr/bin/python
"""Test the instrument query for the uploader policy."""
from os import getenv
from unittest import TestCase
from json import dumps
import httpretty
from policy.uploader.base import QueryBase
from policy import METADATA_ENDPOINT

ADMIN_GROUP = getenv('ADMIN_GROUP', 'admin')


# pylint: disable=too-few-public-methods
class BaseTestData(object):
    """Defines the base user admin bits common to both instrument and proposal tests."""

    sample_user_id = 23
    admin_user_id = 45
    admin_group_id = 127
    user_group_json = [
        {
            'group_id': admin_group_id,
            'person_id': admin_user_id
        }
    ]
    admin_group_json = [
        {
            '_id': admin_group_id
        }
    ]
    group_url = '{0}/groups'.format(METADATA_ENDPOINT)
    user_group_url = '{0}/user_group'.format(METADATA_ENDPOINT)

    def init_admin_urls(self, user_group_json):
        """Setup the admin group and return bits."""
        httpretty.register_uri(httpretty.GET, self.group_url,
                               body=dumps(self.admin_group_json),
                               content_type='application/json')
        httpretty.register_uri(httpretty.GET, self.user_group_url,
                               body=dumps(user_group_json),
                               content_type='application/json')
# pylint: enable=too-few-public-methods


# pylint: disable=too-many-public-methods
class TestBaseQuery(TestCase, BaseTestData):
    """Test the instrument query system."""

    @httpretty.activate
    def test_init(self):
        """Test the GET method using kwargs."""
        httpretty.register_uri(httpretty.GET, self.group_url,
                               body=dumps(self.admin_group_json),
                               content_type='application/json')
        QueryBase()
        last_req = httpretty.last_request()
        self.assertTrue('group_name' in last_req.querystring)
        self.assertTrue(ADMIN_GROUP in last_req.querystring['group_name'])

    @httpretty.activate
    def test_is_admin_false(self):
        """Test the GET method using kwargs."""
        self.init_admin_urls([])
        instq = QueryBase()
        # pylint: disable=protected-access
        self.assertFalse(instq._is_admin(self.sample_user_id))
        # pylint: enable=protected-access
        last_req = httpretty.last_request()
        self.assertTrue('group_id' in last_req.querystring)
        self.assertTrue(str(self.admin_group_id) in last_req.querystring['group_id'])
        self.assertTrue('person_id' in last_req.querystring)
        self.assertTrue(str(self.sample_user_id) in last_req.querystring['person_id'])

    @httpretty.activate
    def test_is_admin_true(self):
        """Test the GET method using kwargs."""
        self.init_admin_urls(self.admin_group_json)
        instq = QueryBase()
        # pylint: disable=protected-access
        self.assertTrue(instq._is_admin(self.admin_user_id))
        # pylint: enable=protected-access
        last_req = httpretty.last_request()
        self.assertTrue('group_id' in last_req.querystring)
        self.assertTrue(str(self.admin_group_id) in last_req.querystring['group_id'])
        self.assertTrue('person_id' in last_req.querystring)
        self.assertTrue(str(self.admin_user_id) in last_req.querystring['person_id'])
