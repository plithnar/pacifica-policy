#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the render object for the search interface."""
from os import getenv
from collections import OrderedDict
import requests
from .globals import METADATA_ENDPOINT

ELASTIC_INDEX = getenv('ELASTIC_INDEX', 'pacifica_search')


class LimitedSizeDict(OrderedDict):
    """Limited caching dictionary."""

    def __init__(self, *args, **kwds):
        """Constructor for caching dictionary."""
        self.size_limit = kwds.pop('size_limit', None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __getitem__(self, key):
        """Get the item and put it back so it's on top."""
        val = OrderedDict.__getitem__(self, key)
        self.__setitem__(key, val)
        return val

    def __setitem__(self, key, value):
        """Set item foo[key] = value."""
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        """Function to set the item and remove old ones."""
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


def trans_science_themes(obj):
    """Render the science theme from a proposal."""
    return [SearchRender.render_science_theme(obj['proposal'])]


def trans_proposals(obj):
    """Render the proposals for a transaction."""
    return [SearchRender.render('proposal', obj['proposal'])],


def trans_inst_groups(obj):
    """Render the instrument groups for a transaction."""
    return SearchRender.get_groups_from_instrument(obj['instrument']),


def trans_instruments(obj):
    """Render the instruments for a transaction."""
    return [
        SearchRender.render(
            'instruments',
            SearchRender.get_obj_by_id('instruments', obj['instrument'])
        )
    ]


def trans_institutions(obj):
    """Render the institutions for a transaction."""
    return SearchRender.get_institutions_from_user(obj['submitter'])


def trans_users(obj):
    """Render the users list for transactions."""
    return [
        SearchRender.render(
            'users',
            SearchRender.get_obj_by_id('users', obj['submitter'])
        )
    ]


class SearchRender(object):
    """Search render class to contain methods."""

    obj_cache = {}
    render_data = {
        'instruments': {
            'display_name': '{display_name}',
            'long_name': '{name}'
        },
        'institutions': {
            'display_name': '{name}'
        },
        'users': {
            'display_name', '{first_name}, {last_name} {middle_initial}'
        },
        'proposals': {
            'display_name': '{title}',
            'long_name': '',
            'abstract': '{abstract}',
            'title': '{title}',
        },
        'groups': {
            'display_name': '{name}'
        },
        'transactions': {
            'users': trans_users,
            'institutions': trans_institutions,
            'instruments': trans_instruments,
            'instrument_groups': trans_inst_groups,
            'proposals': trans_proposals,
            'science_themes': trans_science_themes
        }
    }

    @classmethod
    def get_obj_by_id(cls, obj, obj_id):
        """Get the user from metadata and put it in cache."""
        if obj not in cls.obj_cache:
            cls.obj_cache[obj] = LimitedSizeDict(1000)
        cache = cls.obj_cache[obj]
        if obj_id in cache:
            return cache[obj_id]
        resp = requests.get(
            '{base_url}/{obj}?_id={obj_id}'.format(
                base_url=METADATA_ENDPOINT,
                obj=obj,
                obj_id=obj_id
            )
        )
        cache[obj_id] = resp.json()[0]
        return cache[obj_id]

    @classmethod
    def get_institutions_from_user(cls, user_id):
        """Get an institution list based on user id."""
        resp = requests.get(
            '{base_url}/institution_person?person_id={user_id}'.format(
                base_url=METADATA_ENDPOINT,
                user_id=user_id
            )
        )
        ret = []
        for inst_id in [obj['institution_id'] for obj in resp.json()]:
            ret.append(cls.render('institutions',
                                  cls.get_obj_by_id('institutions', inst_id)))
        return ret

    @classmethod
    def get_groups_from_instrument(cls, inst_id):
        """Get the list of groups from an instrument."""
        resp = requests.get(
            '{base_url}/instrument_group?instrument_id={inst_id}'.format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        ret = []
        for grp_id in [obj['group_id'] for obj in resp.json()]:
            ret.append(cls.render(
                'groups', cls.get_obj_by_id('groups', grp_id)))
        return ret

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_institutions(cls, inst_id):
        """Get a list of transactions from an institution."""
        resp = requests.get(
            '{base_url}/institution_person?institution_id={inst_id}'.format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        ret = []
        for user_id in [obj['person_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_users(user_id))
        return ret
    # pylint: enable=invalid-name

    @classmethod
    def get_transactions_from_users(cls, user_id):
        """Get a list of transactions for a user."""
        resp = requests.get(
            '{base_url}/transactions?submitter={user_id}'.format(
                base_url=METADATA_ENDPOINT,
                user_id=user_id
            )
        )
        return [obj['_id'] for obj in resp.json()]

    @classmethod
    def get_transactions_from_proposals(cls, prop_id):
        """Get a list of transactions for a proposal."""
        resp = requests.get(
            '{base_url}/transactions?proposal={prop_id}'.format(
                base_url=METADATA_ENDPOINT,
                prop_id=prop_id
            )
        )
        return [obj['_id'] for obj in resp.json()]

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_instruments(cls, inst_id):
        """Get a list of transactions for a instrument."""
        resp = requests.get(
            '{base_url}/transactions?instrument={inst_id}'.format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        return [obj['_id'] for obj in resp.json()]
    # pylint: enable=invalid-name

    @classmethod
    def get_transactions_from_groups(cls, group_id):
        """Get a list of instruments for a group."""
        resp = requests.get(
            '{base_url}/instrument_group?group_id={group_id}'.format(
                base_url=METADATA_ENDPOINT,
                group_id=group_id
            )
        )
        ret = []
        for inst_id in [obj['instrument_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_instruments(inst_id))
        return ret

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_science_theme(cls, science_theme):
        """Get a list of transactions for a science theme."""
        resp = requests.get(
            '{base_url}/proposals?science_theme={science_theme}'.format(
                base_url=METADATA_ENDPOINT,
                science_theme=science_theme
            )
        )
        ret = []
        for prop_id in [obj['_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_proposals(prop_id))
        return ret
    # pylint: enable=invalid-name

    @classmethod
    def generate(cls, obj_cls, obj, trans_ids=False):
        """generate the institution object."""
        yield {
            '_op_type': 'update',
            '_index': ELASTIC_INDEX,
            '_type': obj_cls,
            '_id': obj['_id'],
            'doc': getattr(cls, 'render_{}'.format(obj_cls))(obj, trans_ids),
            'doc_as_upsert': True
        }
        if obj_cls == 'proposals':
            yield {
                '_op_type': 'update',
                '_index': ELASTIC_INDEX,
                '_type': 'science_theme',
                '_id': obj['science_theme'],
                'doc': cls.render_science_theme(obj, trans_ids),
                'doc_as_upsert': True
            }

    @classmethod
    def render_science_theme(cls, obj, trans_ids=False):
        """Render the science theme as an object..."""
        ret = {
            'type': 'science_theme',
            'display_name': obj['science_theme']
        }
        if trans_ids:
            ret['transaction_ids'] = cls.get_transactions_from_science_theme(
                obj['science_theme'])
        return ret

    @classmethod
    def render(cls, obj_cls, obj, trans_ids=False):
        """Render the instrument object hash."""
        ret = {
            'type': obj_cls
        }
        for key, value in cls.render_data[obj_cls].items():
            if callable(value):
                ret[key] = value(obj)
            else:
                ret[key] = value.format(**obj)
        if trans_ids:
            trans_func = getattr(
                cls, 'get_transactions_from_{}'.format(obj_cls))
            ret['transaction_ids'] = trans_func(obj['_id'])
        return ret
