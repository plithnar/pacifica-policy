#!/usr/bin/python
"""Common server setup code for CherryPy testing."""
import logging
import cherrypy
from policy.root import Root
from PolicyServer import error_page_default


# pylint: disable=too-few-public-methods
class CommonCPSetup(object):
    """Common CherryPy setup class."""

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
