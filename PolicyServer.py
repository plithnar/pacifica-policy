#!/usr/bin/python

import cherrypy
from wsgiref.simple_server import make_server
from policy.root import Root

CONF = {
  '/': {
    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    'tools.response_headers.on': True,
    'tools.response_headers.headers': [('Content-Type', 'text/plain')],
  }
}
application = cherrypy.Application(Root(), '/', config=CONF)
HTTPD = make_server('0.0.0.0', 8181, application)
HTTPD.serve_forever()
