#!/usr/bin/python
"""CherryPy root object class."""
from policy.uploader.rest import UploaderPolicy


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
# pylint: enable=too-few-public-methods
