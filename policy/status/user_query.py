#!/usr/bin/python
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from policy import METADATA_ENDPOINT, validate_user


# pylint: disable=too-few-public-methods
class UserQuery(object):
    """CherryPy root object class."""

    exposed = True

    @staticmethod
    def _get_user_info(user_id):
        """Return detailed info about a given user."""
        lookup_url = '{0}/userinfo/by_id/{1}'.format(
            METADATA_ENDPOINT, user_id
        )
        return requests.get(url=lookup_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_user('user')
    def GET(**kwargs):
        """CherryPy GET method."""
        user_id = kwargs['user']
        return UserQuery._get_user_info(user_id)
# pylint: enable=too-few-public-methods
