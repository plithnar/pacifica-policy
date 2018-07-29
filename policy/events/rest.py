#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Events rest module for the cherrypy endpoint."""
import cherrypy
from policy.ingest.rest import IngestPolicy


# pylint: disable=too-few-public-methods
class EventsPolicy(IngestPolicy):
    """
    CherryPy Events Policy.

    This exposes whether a user can see an event from.
    """

    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    # pylint: disable=arguments-differ
    def POST(self, username):
        """Pull the json content and validate the user can see the event."""
        event_obj = cherrypy.request.json
        userinfo = self._user_info_from_kwds(
            network_id=username, recursion_depth=0, recursion_limit=1)
        for rec in event_obj['data']:
            if rec['destinationTable'] == 'Transactions.submitter':
                rec['value'] = userinfo[0]['_id']
        return self._valid_query(event_obj['data'])
    # pylint: enable=arguments-differ
# pylint: disable=too-few-public-methods