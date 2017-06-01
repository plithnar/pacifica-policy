#!/usr/bin/python
"""Test the uploader policy."""
from json import dumps, loads
from cherrypy.test import helper
from policy.uploader.rest import UploaderPolicy
from policy.test.test_common import CommonCPSetup


class TestUploaderPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    queries = {
        'user_query': {
            'query': {
                'user': -1,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {'network_id': 'dmlb2001'}
            },
            'answer': [
                {
                    'last_name': 'Brown Jr',
                    'first_name': 'David'
                }
            ]
        },
        'user_query_no_where': {
            'query': {
                'user': 10,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {}
            },
            'answer': [
                {
                    'last_name': 'Brown Jr',
                    'first_name': 'David'
                }
            ]
        },
        'user_query_with_proposal': {
            'query': {
                'user': 10,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {'proposal_id': '1234a', 'user': 10}
            },
            'answer': [
                {
                    'last_name': 'Brown Jr',
                    'first_name': 'David'
                }
            ]
        },
        'proposal_query': {
            'query': {
                'user': 10,
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'proposal_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development (active no close)'
                }
            ]
        },
        'proposal_query_not_admin': {
            'query': {
                'user': 100,
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'proposal_id': '1234b'}
            },
            'answer': [
                {
                    '_id': '1234b',
                    'title': 'Pacifica Development'
                }
            ]
        },
        'proposal_query2': {
            'query': {
                'user': 10,
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development (active no close)'
                }
            ]
        },
        'proposal_query_with_instruments': {
            'query': {
                'user': 11,
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'instrument_id': 74}
            },
            'answer': [
                {
                    '_id': '1234c',
                    'title': 'Pacifica Development (Alt)',
                }
            ]
        },
        'proposal_query_for_user': {
            'query': {
                'user': 10,
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development (active no close)'
                }
            ]
        },
        'instrument_query': {
            'query': {
                'user': 10,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'_id': 54}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': 'NMR PROBES: Nittany Liquid Probes'
                }
            ]
        },
        'instrument_query_from_proposal': {
            'query': {
                'user': 10,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'proposal_id': '1234a'}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': 'NMR PROBES: Nittany Liquid Probes'
                }
            ]
        },
        'instrument_query_from_proposal_bad': {
            'query': {
                'user': 100,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'proposal_id': '1234a'}
            },
            'answer': []
        }
    }

    def test_queries(self):
        """Test posting the queries."""
        for value in self.queries.values():
            self.getPage('/uploader',
                         self.headers + [('Content-Length', str(len(dumps(value['query']))))],
                         'POST',
                         dumps(value['query']))
            self.assertStatus('200 OK')
            self.assertHeader('Content-Type', 'application/json')
            if loads(self.body):
                answer = loads(self.body)[0]
                for akey, avalue in value['answer'][0].items():
                    self.assertTrue(akey in answer)
                    self.assertEqual(avalue, answer[akey])
            else:
                self.assertEqual(len(loads(self.body)), 0)

    def test_bad_query(self):
        """Try to throw a bad query at the query select method."""
        upolicy = UploaderPolicy()
        hit_exception = False
        try:
            # pylint: disable=protected-access
            upolicy._query_select({})
            # pylint: enable=protected-access
        except KeyError:
            hit_exception = True
        self.assertTrue(hit_exception)
        hit_exception = False
        try:
            bad_query = {
                'user': 100,
                'from': 'foo',
                'where': {}
            }
            # pylint: disable=protected-access
            upolicy._query_select(bad_query)
            # pylint: enable=protected-access
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

        bad_queries = [
            {
                'user': 'abcd'
            },
            {
                'user': 'abcd',
                'from': 'users',
                'columns': ['first_name'],
                'where': {'network_id': 'foo'}
            }
        ]
        for bad_query in bad_queries:
            self.getPage('/uploader',
                         self.headers+[('Content-Length', str(len(dumps(bad_query))))],
                         'POST',
                         dumps(bad_query))
            self.assertStatus('500 Internal Server Error')
            hit_exception = False
            try:
                loads(self.body)
            except ValueError:  # pragma no cover
                hit_exception = True
            self.assertFalse(hit_exception)

        # pylint: disable=protected-access
        self.assertFalse(upolicy._valid_query({'foo': 'bar'}))
        self.assertFalse(upolicy._valid_query({'user': 'bar', 'from': 'baz'}))
        # pylint: enable=protected-access
