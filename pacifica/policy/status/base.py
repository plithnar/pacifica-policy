#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Base class module for standard queries for the upload status tool."""
import requests
from pacifica.policy.config import get_config
from pacifica.policy.admin import AdminPolicy


# pylint: disable=too-few-public-methods
class QueryBase(AdminPolicy):
    """This pulls the common bits of instrument and project query into a single class."""

    md_url = get_config().get('metadata', 'endpoint_url')
    all_instruments_url = '{0}/instruments'.format(md_url)
    all_projects_url = '{0}/projects'.format(md_url)
    all_transactions_url = '{0}/transactions'.format(md_url)

    proj_participant_url = '{0}/project_participant'.format(md_url)
    proj_instrument_url = '{0}/project_instrument'.format(md_url)

    @staticmethod
    def _get_available_projects(user_id):
        md_url = '{0}/project_participant'.format(
            get_config().get('metadata', 'endpoint_url')
        )
        params = {
            'person_id': user_id
        }
        response = requests.get(url=md_url, params=params)

        return [x.get('project_id') for x in response.json()]
# pylint: enable=too-few-public-methods
