#!/usr/bin/python
"""
Test the instrument query for the uploader policy
"""
from unittest import TestCase
import httpretty
from policy.root import Root
from policy.uploader.test.base import BaseTestData

class TestRoot(TestCase):
    """
    Test the root of the CherryPy obj tree
    """
    @httpretty.activate
    def test_create(self):
        """
        Create a root object
        """
        prep = BaseTestData()
        prep.init_admin_urls([])
        root = Root()
        self.assertTrue(root is not None)
