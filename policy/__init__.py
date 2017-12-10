#!/usr/bin/python
"""
This is the policy module.

This module is organized by workflow type used by each subproject
of the overall Pacifica software... So there's an uploader module
under which are queries that you can apply policy to to change the
behavour of the uploader.
"""
from __future__ import print_function, absolute_import
import sys
from json import dumps
import cherrypy
from .root import Root
from .globals import CHERRYPY_CONFIG


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    json_str = dumps({
        'postdata': cherrypy.request.body.read(),
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    }, sort_keys=True, indent=4)
    print(json_str, file=sys.stderr)
    return json_str


def main():
    """Main method to start the httpd server."""
    cherrypy.quickstart(Root(), '/', CHERRYPY_CONFIG)
