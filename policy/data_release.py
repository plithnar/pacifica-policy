#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data release policy for command line tools."""
from __future__ import print_function
from datetime import datetime
from json import dumps
from dateutil import parser
from six import text_type
import requests
from .globals import METADATA_ENDPOINT

VALID_KEYWORDS = [
    'proposals.actual_end_date',
    'proposals.actual_start_date',
    'proposals.submitted_date',
    'proposals.accepted_date',
    'proposals.closed_date',
    'transactions.created',
    'transactions.updated'
]


def relavent_data_release_objs(time_ago, orm_obj, date_key):
    """generate a list of relavent orm_objs saving date_key."""
    objs = {}
    for time_field in ['updated', 'created']:
        resp = requests.get(
            text_type('{base_url}/{orm_obj}?{time_field}={epoch}&{time_field}_operator=gt').format(
                base_url=METADATA_ENDPOINT,
                time_field=time_field,
                orm_obj=orm_obj,
                epoch=(
                    datetime.now() - time_ago
                ).replace(microsecond=0).isoformat()
            )
        )
        for chk_obj in resp.json():
            if chk_obj['_id'] not in objs.keys() and chk_obj.get(date_key, False):
                objs[chk_obj['_id']] = chk_obj[date_key]
    return objs


def update_data_release_objs(objs, time_after, orm_obj):
    """update the list of objs given date_key adding time_after."""
    for obj_id, obj_date_key in objs.items():
        resp = requests.post(
            text_type('{base_url}/{orm_obj}?_id={obj_id}').format(
                base_url=METADATA_ENDPOINT,
                orm_obj=orm_obj,
                obj_id=obj_id
            ),
            data=dumps(
                {
                    '_id': obj_id,
                    'suspense_date': (
                        parser.parse(obj_date_key) + time_after
                    ).replace(microsecond=0).isoformat()
                }
            ),
            headers={'content-type': 'application/json'}
        )
        assert resp.status_code == 200


def data_release(args):
    """
    Data release main subcommand.

    The logic is to query updated objects between now and
    args.time_ago. If the objects args.keyword is set to something
    calculate the suspense date as args.time_after the keyword date.
    Then save the object back to the metadata server.
    """
    orm_obj, date_key = args.keyword.split('.')
    objs = relavent_data_release_objs(args.time_ago, orm_obj, date_key)
    update_data_release_objs(objs, args.time_after, orm_obj)
