"""CherryPy Status Policy object class."""
import requests
from cherrypy import tools, HTTPError
from policy.validation import validate_proposal
from policy.globals import METADATA_ENDPOINT
from policy.status.base import QueryBase


# pylint: disable=too-few-public-methods
class InstrumentsByProposal(QueryBase):
    """Retrieves instrument list for a given proposal."""

    exposed = True

    @staticmethod
    def _get_instruments_for_proposal(proposal_id):
        """Return a list with all the instruments belonging to this proposal."""
        md_url = u'{0}/proposalinfo/by_proposal_id/{1}'.format(
            METADATA_ENDPOINT, proposal_id
        )
        query = requests.get(url=md_url)
        if query.status_code == 200:
            return query.json()
        elif query.status_code == 404:
            raise HTTPError('404 Not Found')

    # CherryPy requires these named methods
    # Add HEAD (basically Get without returning body
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @validate_proposal()
    def GET(proposal_id=None):
        """CherryPy GET method."""
        proposal_info = InstrumentsByProposal._get_instruments_for_proposal(proposal_id)
        instruments = {index: info for (index, info) in proposal_info.get('instruments').items()}
        cleaned_instruments = []
        if instruments:
            clean_info = {
                'id': -1,
                'text': u'All Available Instruments for Proposal {0}'.format(proposal_id),
                'name': 'All Instruments',
                'active': 'Y'
            }
            cleaned_instruments.append(clean_info)

        for inst_id in instruments.keys():
            info = instruments.get(inst_id)
            clean_info = {
                'id': inst_id,
                'text': u'Instrument {0}: {1}'.format(inst_id, info.get('display_name')),
                'name': info.get('name_short'),
                'active': 'Y' if info.get('active') else 'N'
            }
            cleaned_instruments.append(clean_info)

        return_block = {
            'total_count': len(cleaned_instruments),
            'incomplete_results': False,
            'items': cleaned_instruments
        }
        return return_block
# pylint: enable=too-few-public-methods
