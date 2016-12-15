#!/usr/bin/python
"""Test the uploader policy."""
from json import dumps, loads
import logging
import cherrypy
from cherrypy.test import helper
from policy.root import Root
from policy.uploader.rest import UploaderPolicy
from PolicyServer import error_page_default


class TestUploaderPolicy(helper.CPWebCase):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    queries = {
        'user_query': {
            'query': {
                'user': 'dmlb2001',
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
                'user': 'dmlb2001',
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
                'user': 'dmlb2001',
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {'proposal_id': '1234a'}
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
                'user': 'dmlb2001',
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'proposal_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development'
                }
            ]
        },
        'proposal_query_not_admin': {
            'query': {
                'user': 'dmlb2000',
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
                'user': 'dmlb2001',
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development'
                }
            ]
        },
        'proposal_query_with_instruments': {
            'query': {
                'user': 'dmlb2001',
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {'instrument_id': 54}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development'
                }
            ]
        },
        'proposal_query_for_user': {
            'query': {
                'user': 'dmlb2001',
                'from': 'proposals',
                'columns': ['_id', 'title'],
                'where': {}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': 'Pacifica Development'
                }
            ]
        },
        'instrument_query': {
            'query': {
                'user': 'dmlb2001',
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
                'user': 'dmlb2001',
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
                'user': 'dmlb2000',
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'proposal_id': '1234a'}
            },
            'answer': []
        }
    }

    @staticmethod
    def setup_server():
        """Setup each test by starting the CherryPy server."""
        logger = logging.getLogger('urllib2')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update('server.conf')
        cherrypy.tree.mount(Root(), '/', 'server.conf')

    def test_queries(self):
        """Test posting the queries."""
        for value in self.queries.values():
            self.getPage('/uploader',
                         self.headers+[('Content-Length', str(len(dumps(value['query']))))],
                         'POST',
                         dumps(value['query']))
            self.assertStatus('200 OK')
            self.assertHeader('Content-Type', 'application/json')
            if len(loads(self.body)):
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
                'user': 'dmlb2000',
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
                'user': 'dmlb2001'
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
