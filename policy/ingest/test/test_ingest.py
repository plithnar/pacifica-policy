#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ingest with httpretty."""
from os.path import join
from json import loads
import httpretty
from policy.ingest.rest import IngestPolicy
from policy.uploader.test.test_uploader import TestUploader


class TestIngest(TestUploader):
    """Test the ingest policy with httpretty."""

    @httpretty.activate
    def test_failed_admin_id(self):
        """override this to test valid query."""
        super(TestIngest, self).test_failed_admin_id()
        valid_query = loads(open(join('test_files', 'ingest_base_query.json')).read())
        ipolicy = IngestPolicy()
        # pylint: disable=no-member
        # pylint: disable=protected-access
        ret = ipolicy._valid_query(valid_query)
        self.assertTrue(ret)
        valid_query[1]['value'] = 100
        ret = ipolicy._valid_query(valid_query)
        self.assertTrue(ret)
        # pylint: enable=protected-access
        # pylint: enable=no-member
