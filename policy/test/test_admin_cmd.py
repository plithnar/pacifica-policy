#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the admin command line."""
from unittest import TestCase
import requests
from ..admin_cmd import main


class TestAdminCMD(TestCase):
    """Test the admin command line tools."""

    def test_default_search_sync(self):
        """Test the data release subcommand."""
        main('searchsync')
        resp = requests.get('http://localhost:9200/pacifica_search/_stats')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.json()['indices']['pacifica_search']['primaries']['docs']['count'], 22)

    def test_default_data_release(self):
        """Test the data release subcommand."""
        main('data_release', '--time-after', '365 days after')
        resp = requests.get('http://localhost:8121/proposals?_id=1234a')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]['suspense_date'], '2018-09-29')
