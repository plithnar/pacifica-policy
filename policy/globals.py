#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global static variables."""
from os import getenv


CHERRYPY_CONFIG = getenv('CHERRYPY_CONFIG', 'server.conf')
DEFAULT_METADATA_ENDPOINT = getenv(
    'METADATA_PORT', 'tcp://127.0.0.1:8121').replace('tcp', 'http')
METADATA_ENDPOINT = getenv('METADATA_ENDPOINT', DEFAULT_METADATA_ENDPOINT)
METADATA_CONNECT_ATTEMPTS = 40
METADATA_WAIT = 3
METADATA_STATUS_URL = '{0}/groups'.format(METADATA_ENDPOINT)

MATCH_VALIDATORS = {
    'proposal': r'[0-9]+[a-zA-Z]*',
    'user': r'[0-9]+',
    'transaction': r'[0-9]+'
}
