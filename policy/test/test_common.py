#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Common server setup code for CherryPy testing."""
import logging
from json import dumps, loads
import cherrypy
from cherrypy.test import helper
from policy.root import Root
from policy import error_page_default


# pylint: disable=too-few-public-methods
class CommonCPSetup(helper.CPWebCase):
    """Common CherryPy setup class."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def get_json_page(self, path, valid_query):
        """Get a json page and validate its return format."""
        self.getPage(path,
                     self.headers +
                     [('Content-Length', str(len(dumps(valid_query))))],
                     'POST',
                     dumps(valid_query))
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
        return loads(self.body.decode('UTF-8'))

    @staticmethod
    def setup_server():
        """Setup each test by starting the CherryPy server."""
        logger = logging.getLogger('urllib2')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update('server.conf')
        cherrypy.tree.mount(Root(), '/', 'server.conf')
# pylint: enable=too-few-public-methods
