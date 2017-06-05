#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader policy."""
from cherrypy.test import helper
from policy.test.test_common import CommonCPSetup
from policy.admin import AdminPolicy


class TestAdminBase(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_base_queries(self):
        """Test the base class queries."""
        adm_policy = AdminPolicy()
        # pylint: disable=protected-access
        res = adm_policy._proposals_for_custodian(10)
        # pylint: enable=protected-access
        self.assertTrue('1234a' in res)
