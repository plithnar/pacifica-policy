#!/usr/bin/python
"""CherryPy root object class."""
from policy.uploader.rest import UploaderPolicy
from policy.status.rest import StatusPolicy
from policy.ingest.rest import IngestPolicy


# pylint: disable=too-few-public-methods
class Root(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed
    """

    exposed = False

    def __init__(self):
        """Create the local objects we need."""
        self.uploader = UploaderPolicy()
        self.status = StatusPolicy()
        self.ingest = IngestPolicy()
# pylint: enable=too-few-public-methods
