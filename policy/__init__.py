#!/usr/bin/python
"""
This is the policy module

This module is organized by workflow type used by each subproject
of the overall Pacifica software... So there's an uploader module
under which are queries that you can apply policy to to change the
behavour of the uploader.
"""
from os import getenv
from time import sleep
import requests

DEFAULT_METADATA_ENDPOINT = getenv('METADATA_PORT', 'tcp://127.0.0.1:8121').replace('tcp', 'http')
METADATA_ENDPOINT = getenv('METADATA_ENDPOINT', DEFAULT_METADATA_ENDPOINT)
METADATA_CONNECT_ATTEMPTS = 10
METADATA_WAIT = 1
METADATA_STATUS_URL = "%s/groups"%(METADATA_ENDPOINT)

def try_meta_connect(attempts=0):
    """
    try to connect to the metadata service see if its there
    """
    try:
        ret = requests.get(METADATA_STATUS_URL.encode('utf-8'))
        if ret.status_code != 200:
            raise Exception("try_meta_connect: %s\n"%(ret.status_code))
    # pylint: disable=broad-except
    except Exception, ex:
        # pylint: enable=broad-except
        if attempts < METADATA_CONNECT_ATTEMPTS:
            sleep(METADATA_WAIT)
            attempts += 1
            try_meta_connect(attempts)
        else:
            raise ex
