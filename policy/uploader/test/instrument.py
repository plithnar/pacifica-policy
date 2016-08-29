#!/usr/bin/python
"""
Test the instrument query for the uploader policy
"""
from unittest import TestCase
from json import dumps
from policy.uploader.instrument import InstrumentQuery

# pylint: disable=too-many-public-methods
class TestInstrumentQuery(TestCase):
    """
    Test the instrument query system
    """
    def test_get_kwargs(self):
        """
        Test the GET method using kwargs
        """
        data = [{
            'self_type': 'InstrumentQuery',
            'user_id': 1234,
            'proposal_id': '1234a'
        }]
        instq = InstrumentQuery()
        ret = instq.GET(user_id=1234, proposal_id="1234a")
        self.assertEqual(ret, dumps(data))

    def test_get_kwargs_no_prop(self):
        """
        Test the GET method using kwargs
        """
        data = [{
            'self_type': 'InstrumentQuery',
            'user_id': 1234,
            'proposal_id': None
        }]
        instq = InstrumentQuery()
        ret = instq.GET(user_id=1234)
        self.assertEqual(ret, dumps(data))
