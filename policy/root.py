#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy root object class."""
from time import sleep
import requests
from policy.uploader.rest import UploaderPolicy
from policy.status.rest import StatusPolicy
from policy.ingest.rest import IngestPolicy
from policy.reporting.rest import ReportingPolicy
from policy.globals import METADATA_STATUS_URL, METADATA_CONNECT_ATTEMPTS, METADATA_WAIT


# pylint: disable=too-few-public-methods
class Root(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = False

    def __init__(self):
        """Create the local objects we need."""
        self._try_meta_connect()
        self.uploader = UploaderPolicy()
        self.status = StatusPolicy()
        self.reporting = ReportingPolicy()
        self.ingest = IngestPolicy()

    @classmethod
    def _try_meta_connect(cls, attempts=0):
        """Try to connect to the metadata service see if its there."""
        try:
            ret = requests.get(METADATA_STATUS_URL.encode('utf-8'))
            if ret.status_code != 200:
                raise Exception(
                    'try_meta_connect: {0}\n'.format(ret.status_code))
        # pylint: disable=broad-except
        except Exception:
            # pylint: enable=broad-except
            if attempts < METADATA_CONNECT_ATTEMPTS:
                sleep(METADATA_WAIT)
                attempts += 1
                cls._try_meta_connect(attempts)
            else:
                raise Exception
# pylint: enable=too-few-public-methods
