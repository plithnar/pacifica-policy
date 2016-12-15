#!/usr/bin/python
"""
The CherryPy rest object for the structure.

[
  {"destinationTable": "Transactions._id", "value": 1234},
  {"destinationTable": "Transactions.submitter", "value": 34002},
  {"destinationTable": "Transactions.proposal", "value": "34002"},
  {"destinationTable": "Transactions.instrument", "value": 34002},
  {"destinationTable": "TransactionKeyValue", "key": "Tag", "value": "Blah"},
  {"destinationTable": "TransactionKeyValue", "key": "Taggy", "value": "Blah"},
  {"destinationTable": "TransactionKeyValue", "key": "Taggier", "value": "Blah"}
  {
    "destinationTable": "Files",
    "_id": 34, "name": "foo.txt", "subdir": "a/b/",
    "ctime": "Tue Nov 29 14:09:05 PST 2016",
    "mtime": "Tue Nov 29 14:09:05 PST 2016",
    "size": 128, "mimetype": "text/plain"
  },
  {
    "destinationTable": "Files",
    "_id": 35, "name": "bar.txt", "subdir": "a/b/",
    "ctime": "Tue Nov 29 14:09:05 PST 2016",
    "mtime": "Tue Nov 29 14:09:05 PST 2016",
    "size": 47, "mimetype": "text/plain"
  },
]
"""
from cherrypy import tools, request, HTTPError
from policy.uploader.rest import UploaderPolicy


# pylint: disable=too-few-public-methods
class IngestPolicy(UploaderPolicy):
    """CherryPy Ingest Policy Class."""

    def _valid_query(self, query):
        """Validate the metadata format."""
        try:
            submitter_id = [x['value'] for x in query if x['destinationTable'] == 'Transactions.submitter'][0]
            proposal_id = [x['value'] for x in query if x['destinationTable'] == 'Transactions.proposal'][0]
            instrument_id = [x['value'] for x in query if x['destinationTable'] == 'Transactions.instrument'][0]
            if proposal_id not in self._proposals_for_user_inst(submitter_id, instrument_id):
                return False
        except (KeyError, ValueError, IndexError):
            return False
        return True

    # pylint: disable=invalid-name
    @tools.json_in()
    @tools.json_out()
    def POST(self):
        """Read in the json query and return results."""
        metadata = request.json
        if not self._valid_query(metadata):
            raise HTTPError(500, 'Invalid Metadata.')
        return {'status': 'success'}
    # pylint: enable=invalid-name
# pylint: enable=too-few-public-methods
