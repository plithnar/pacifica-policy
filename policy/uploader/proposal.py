#!/usr/bin/python
"""
CherryPy Uploader Policy object class
"""
from json import dumps

# pylint: disable=too-few-public-methods
class ProposalQuery(object):
    """
    CherryPy root object class

    not exposed by default the base objects are exposed
    """
    exposed = True
    def _get(self, user_id, instrument_id=None):
        """
        Return the list of proposals given the user and
        an optional instrument_id
        """
        return dumps([{
            'self_type': self.__class__.__name__,
            'user_id': user_id,
            'instrument_id': instrument_id
        }])

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    def GET(self, *args, **kwargs):
        """
        CherryPy GET method
        """
        user_id = None
        instrument_id = None
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        if 'instrument_id' in kwargs:
            instrument_id = kwargs['instrument_id']
        if len(args) > 0:
            user_id = args[0]
        if len(args) > 1:
            instrument_id = args[1]
        return self._get(user_id, instrument_id)
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
