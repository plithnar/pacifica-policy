#!/usr/bin/python
"""
CherryPy root object class
"""
from policy.uploader import UploaderPolicy

# pylint: disable=too-few-public-methods
class Root(object):
    """
    CherryPy root object class

    not exposed by default the base objects are exposed
    """
    exposed = False
    uploader = UploaderPolicy()
# pylint: enable=too-few-public-methods
