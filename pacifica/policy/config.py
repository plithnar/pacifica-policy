#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
from os import getenv
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import SafeConfigParser
from pacifica.policy.globals import CONFIG_FILE


def get_config():
    """
    Return the ConfigParser object with defaults set.

    Currently metadata API doesn't work with SQLite the queries are
    too complex and it only is supported with MySQL and PostgreSQL.
    """
    configparser = SafeConfigParser()
    configparser.add_section('metadata')
    configparser.set(
        'metadata', 'endpoint_url',
        getenv(
            'METADATA_URL',
            'http://localhost:8121'
        )
    )
    configparser.set(
        'metadata', 'status_url',
        getenv(
            'STATUS_URL',
            'http://localhost:8121/groups'
        )
    )
    configparser.read(CONFIG_FILE)
    return configparser
