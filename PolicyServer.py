#!/usr/bin/python
"""This is the main policy server script."""
from wsgiref.simple_server import make_server
import cherrypy
from policy.root import Root
from policy import try_meta_connect


def main():
    """Main method to start the httpd server."""
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }
    try_meta_connect()
    application = cherrypy.Application(Root(), '/', config=conf)
    httpd = make_server('0.0.0.0', 8181, application)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
