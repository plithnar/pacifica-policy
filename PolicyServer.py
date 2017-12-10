#!/usr/bin/python
"""This is the main policy server script."""
import cherrypy
from policy.root import Root
from policy import main, error_page_default, CHERRYPY_CONFIG


cherrypy.config.update({'error_page.default': error_page_default})
# pylint doesn't realize that application is actually a callable
# pylint: disable=invalid-name
application = cherrypy.Application(Root(), '/', CHERRYPY_CONFIG)
# pylint: enable=invalid-name
if __name__ == '__main__':
    main()
