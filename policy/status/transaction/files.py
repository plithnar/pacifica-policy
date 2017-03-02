"""CherryPy Status Policy object class."""
from cherrypy import tools
import requests
from policy import METADATA_ENDPOINT, validate_transaction


# pylint: disable=too-few-public-methods
class FileLookup(object):
    """Retrieves files for a given transaction_id."""

    exposed = True

    @staticmethod
    def _get_file_list(transaction_id=None):
        """Return files for the specified transaction entry."""
        filelist_url = '{0}/transactioninfo/files/{1}'.format(METADATA_ENDPOINT, transaction_id)
        return requests.get(url=filelist_url).json()

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_transaction()
    def GET(transaction_id=None):
        """CherryPy GET method."""
        return FileLookup._get_file_list(transaction_id)
# pylint: enable=too-few-public-methods