#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test status policy methods."""
from json import loads, dumps
from cherrypy.test import helper
from policy.test.test_common import CommonCPSetup


class TestStatusPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the status policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_instrument_by_proposal(self):
        """Return instruments for a specified proposal."""
        url = '/status/instrument/by_proposal_id/1234a'
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer.get('items')), 2)

    def test_files_for_transaction(self):
        """Return file listing for a transaction."""
        transaction_id = 67
        url = '/status/transactions/files/{0}'.format(transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 2)
        self.assertListEqual(sorted(answer.keys()), sorted(loads(dumps(['103', '104']))))

    def test_transaction_for_id(self):
        """Return transaction info for a given id."""
        transaction_id = 68
        url = '/status/transactions/by_id/{0}'.format(transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(answer['_id'], 68)

        bad_transaction_id = 'bob'
        url = '/status/transactions/by_id/{0}'.format(bad_transaction_id)
        self.getPage(url)
        self.assertStatus('400 Invalid Request')
        self.assertInBody('Provide an appropriate transaction_id')

    def test_transaction_search(self):
        """Return proposals for a specified user."""
        transaction_id = 68
        url = '/status/transactions/search?transaction={0}'.format(transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')

    def test_user_query(self):
        """Test user details retrieval."""
        user_id = 10
        url = '/status/users?user={0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')

    def test_proposals_by_user(self):
        """Return proposals for a specified user."""
        user_id = 10
        url = '/status/proposals/by_user_id/{0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 1)

        user_id = 11
        url = '/status/proposals/by_user_id/{0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        self.assertInBody('404 User Does Not Exist')

    def test_proposal_lookup(self):
        """Return an appropriate proposal for a specified proposal_id."""
        proposal_id = '1234a'
        url = '/status/proposals/by_proposal_id/{0}'.format(proposal_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer['instruments']), 1)
        self.assertEqual(answer['id'], proposal_id)

    def test_proposal_search(self):
        """Return appropriate proposals for a search term and user id."""
        search_term = 'expired'
        user_id = 10  # admin user
        url = '/status/proposals/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 2)

        search_term = None
        url = '/status/proposals/search?user={0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 1)

        search_term = 'pacifica'
        user_id = 100  # non admin user
        url = '/status/proposals/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 1)

        search_term = 'bob'
        url = '/status/proposals/search/{0}'.format(search_term)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 0)

        search_term = 'bob'
        url = '/status/proposals/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 0)

        url = '/status/proposals/search?user_id={0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body)
        self.assertEqual(len(answer), 0)
