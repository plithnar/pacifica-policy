#!/usr/bin/python
"""
This is the policy module.

This module is organized by workflow type used by each subproject
of the overall Pacifica software... So there's an uploader module
under which are queries that you can apply policy to to change the
behavour of the uploader.
"""
import re
from os import getenv
from functools import wraps
from time import sleep
import cherrypy
import requests

DEFAULT_METADATA_ENDPOINT = getenv('METADATA_PORT', 'tcp://127.0.0.1:8121').replace('tcp', 'http')
METADATA_ENDPOINT = getenv('METADATA_ENDPOINT', DEFAULT_METADATA_ENDPOINT)
METADATA_CONNECT_ATTEMPTS = 40
METADATA_WAIT = 3
METADATA_STATUS_URL = '{0}/groups'.format(METADATA_ENDPOINT)

MATCH_VALIDATORS = {
    'proposal': r'[0-9]+[a-zA-Z]*',
    'user': r'[0-9]+',
    'transaction': r'[0-9]+'
}


def try_meta_connect(attempts=0):
    """Try to connect to the metadata service see if its there."""
    try:
        ret = requests.get(METADATA_STATUS_URL.encode('utf-8'))
        if ret.status_code != 200:
            raise Exception('try_meta_connect: {0}\n'.format(ret.status_code))
    # pylint: disable=broad-except
    except Exception as ex:
        # pylint: enable=broad-except
        if attempts < METADATA_CONNECT_ATTEMPTS:
            sleep(METADATA_WAIT)
            attempts += 1
            try_meta_connect(attempts)
        else:
            raise ex


def validate_user(index=0):
    """Validate the user id."""
    return validate_universal(index, 'user')


def validate_transaction(index=0):
    """Validate the transaction id."""
    return validate_universal(index, 'transaction')


def validate_proposal(index=0):
    """Validate the proposal id."""
    return validate_universal(index, 'proposal')


def validate_universal(index, regex):
    """Decorator generator to validate proposal field."""
    def decorator(func):
        """Wrapped decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapped function."""
            try:
                check_id = args[int(index)]
            except ValueError:
                check_id = kwargs[str(index)]
            if not re.match(MATCH_VALIDATORS[regex], check_id):
                message = 'Provide an appropriate {0}_id value'.format(regex)
                raise cherrypy.HTTPError(
                    '400 Invalid Request', message)
            return func(*args, **kwargs)
        return wrapper
    return decorator
