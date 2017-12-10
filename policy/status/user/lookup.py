#!/usr/bin/python
"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from policy.validation import validate_user
from policy.globals import METADATA_ENDPOINT


# pylint: disable=too-few-public-methods
class UserLookup(object):
    """Retrieves info for the specified user."""

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
    @validate_user()
    def GET(user_id=None):
        """CherryPy GET method."""
        return UserLookup._get_user_info(user_id)
# pylint: enable=too-few-public-methods
