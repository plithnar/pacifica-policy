#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader policy."""
from os.path import join
from json import dumps, loads
from cherrypy.test import helper
from policy.test.test_common import CommonCPSetup


class TestIngestPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_queries(self):
        """Test posting the queries."""
        valid_query = loads(open(join('test_files', 'ingest_base_query.json')).read())
        self.getPage('/ingest',
                     self.headers+[('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
        ret_data = loads(self.body)
        self.assertFalse(ret_data is None)
        self.assertTrue('status' in ret_data)
        self.assertEqual(ret_data['status'], 'success')

        # change proposal to valid but he's an admin so this works
        valid_query[4]['key'] = 'Tag'
        valid_query[2]['value'] = '1234a'
        self.getPage('/ingest',
                     self.headers+[('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('200 OK')

        valid_query[1]['value'] = 100
        self.getPage('/ingest',
                     self.headers+[('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('500 Internal Server Error')

        del valid_query[1]['value']
        self.getPage('/ingest',
                     self.headers+[('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('500 Internal Server Error')
