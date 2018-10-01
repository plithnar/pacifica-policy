#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Sync the database to elasticsearch index for use by Searching tools."""
from __future__ import print_function, absolute_import
from os import getenv
from json import dumps
from time import sleep
from threading import Thread
try:
    from Queue import Queue
except ImportError:  # pragma: no cover
    from queue import Queue
from math import ceil
from datetime import datetime
import requests
from six import text_type
from elasticsearch import Elasticsearch, helpers, ElasticsearchException
from .globals import METADATA_ENDPOINT
from .root import Root
from .search_render import ELASTIC_INDEX, SearchRender

ELASTIC_CONNECT_ATTEMPTS = 40
ELASTIC_WAIT = 3
ELASTIC_ENDPOINT = getenv('ELASTIC_ENDPOINT', '127.0.0.1')
SYNC_OBJECTS = [
    'transactions',
    'proposals',
    'users',
    'instruments',
    'institutions',
    'groups'
]


def es_client():
    """Get the elasticsearch client object."""
    esclient = Elasticsearch(
        [ELASTIC_ENDPOINT],
        sniff_on_start=True,
        sniff_on_connection_fail=True,
        sniffer_timeout=60,
        timeout=60
    )
    mapping_params = {
        'properties': {
            'transaction_ids': {
                'type':     'text',
                'fielddata': True
            },
            'users': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },

                }
            },
            'instruments': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },

                }
            },
            'proposals': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },

                }
            },
            'institutions': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },

                }
            },
            'science_themes': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },

                }
            },
            'instrument_groups': {
                'properties': {
                    'keyword': {
                        'type': 'keyword'
                    },
                }
            }
        }
    }
    # pylint: disable=unexpected-keyword-arg
    esclient.indices.create(index=ELASTIC_INDEX, ignore=400)
    esclient.indices.put_mapping(
        index=ELASTIC_INDEX, doc_type='doc', body=dumps(mapping_params))
    # pylint: enable=unexpected-keyword-arg
    return esclient


def try_es_connect(attempts=0):
    """Recursively try to connect to elasticsearch."""
    try:
        cli = es_client()
        cli.info()
    except ElasticsearchException as ex:  # pragma: no cover pulled from metadata
        if attempts < ELASTIC_CONNECT_ATTEMPTS:
            sleep(ELASTIC_WAIT)
            attempts += 1
            try_es_connect(attempts)
        else:
            raise ex


def start_work(work_queue):
    """The main thread for the work."""
    cli = es_client()
    job = work_queue.get()
    while job:
        print('Starting {} ({}): {}'.format(job[0], job[1], job[2]))
        try_doing_work(cli, job)
        work_queue.task_done()
        print('Finished {} ({}): {}'.format(job[0], job[1], job[2]))
        job = work_queue.get()
    work_queue.task_done()


def try_doing_work(cli, job):
    """Try doing some work even if you fail."""
    tries_left = 5
    success = False
    while not success and tries_left:
        try:
            helpers.bulk(cli, yield_data(*job))
            success = True
        except ElasticsearchException:  # pragma: no cover
            tries_left -= 1
    return success


def yield_data(obj, time_field, page, items_per_page, time_delta):
    """yield objects from obj for bulk ingest."""
    get_args = {
        '{time_field}': '{epoch}',
        '{time_field}_operator': 'gt',
        'page_number': '{page}',
        'items_per_page': '{items_per_page}',
        'recursion_depth': '0',
        'recursion_limit': '1'
    }
    get_list = ['{}={}'.format(key, val) for key, val in get_args.items()]
    url = '{base_url}/{orm_obj}?'+'&'.join(get_list)
    resp = requests.get(
        text_type(url).format(
            base_url=METADATA_ENDPOINT,
            orm_obj=obj,
            time_field=time_field,
            epoch=time_delta.isoformat(),
            page=page,
            items_per_page=items_per_page
        )
    )
    objs = resp.json()
    return SearchRender.generate(obj, objs, obj != 'transactions')


def create_worker_threads(threads, work_queue):
    """Create the worker threads and return the list."""
    work_threads = []
    for i in range(threads):
        wthread = Thread(target=start_work, args=(work_queue,))
        wthread.daemon = True
        wthread.start()
        work_threads.append(wthread)
    return work_threads


def generate_work(items_per_page, work_queue, time_ago):
    """Generate the work from the db and send it to the work queue."""
    now = datetime.now()
    time_delta = (now - time_ago).replace(microsecond=0)
    for obj in SYNC_OBJECTS:
        for time_field in ['created', 'updated']:
            resp = requests.get(
                text_type('{base_url}/objectinfo/{orm_obj}?{time_field}={epoch}&{time_field}_operator=gt').format(
                    base_url=METADATA_ENDPOINT,
                    time_field=time_field,
                    orm_obj=obj,
                    epoch=time_delta.isoformat()
                )
            )
            total_count = resp.json()['record_count']
            num_pages = int(ceil(float(total_count) / items_per_page))
            for page in range(1, num_pages + 1):
                work_queue.put(
                    (obj, time_field, page, items_per_page, time_delta))


def search_sync(args):
    """Main search sync subcommand."""
    try_es_connect()
    Root.try_meta_connect()
    work_queue = Queue(32)
    work_threads = create_worker_threads(args.threads, work_queue)
    generate_work(args.items_per_page, work_queue, args.time_ago)
    for i in range(args.threads):
        work_queue.put(False)
    for wthread in work_threads:
        wthread.join()
    work_queue.join()
