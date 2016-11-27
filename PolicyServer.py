#!/usr/bin/python
"""This is the main policy server script."""
import cherrypy
from policy.root import Root
from policy import try_meta_connect


def main():
    """Main method to start the httpd server."""
    try_meta_connect()
    cherrypy.quickstart(Root(), '/', 'server.conf')


if __name__ == '__main__':
    main()
