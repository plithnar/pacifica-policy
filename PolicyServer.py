#!/usr/bin/python
"""This is the main policy server script."""
from __future__ import print_function
import sys
from json import dumps
import cherrypy
from policy.root import Root
from policy import try_meta_connect


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
    try_meta_connect()
    cherrypy.quickstart(Root(), '/', 'server.conf')


cherrypy.config.update({'error_page.default': error_page_default})
# pylint doesn't realize that application is actually a callable
# pylint: disable=invalid-name
application = cherrypy.Application(Root(), '/', 'server.conf')
# pylint: enable=invalid-name
if __name__ == '__main__':
    main()
