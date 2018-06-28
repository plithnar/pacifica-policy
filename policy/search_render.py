#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the render object for the search interface."""
from os import getenv
import sys
from numbers import Number
from collections import OrderedDict, Set, Mapping, deque
from six import text_type
import requests
from .globals import METADATA_ENDPOINT


ELASTIC_INDEX = getenv('ELASTIC_INDEX', 'pacifica_search')
CACHE_SIZE = getenv('CACHE_SIZE', 4000000)


class LimitedSizeDict(OrderedDict):
    """Limited caching dictionary."""

    _seen_ids = set()

    def __init__(self, *args, **kwds):
        """Constructor for caching dictionary."""
        self.size_limit = kwds.pop('size_limit', None)
        self.cur_size = 0
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __getitem__(self, key):
        """Get the item and put it back so it's on top."""
        val = OrderedDict.__getitem__(self, key)
        try:
            del self[key]
            OrderedDict.__setitem__(self, key, val)
        except KeyError:  # pragma: no cover can't get this covered
            # the key must have gotten purged...
            pass
        return val

    # pylint: disable=signature-differs
    def __setitem__(self, key, value):
        """Set item foo[key] = value."""
        self.cur_size += self._getsize(value)
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()
    # pylint: enable=signature-differs

    def _check_size_limit(self):
        """Function to set the item and remove old ones."""
        if self.size_limit is not None:
            while self.cur_size > self.size_limit:
                key, value = self.popitem(last=False)
                self.cur_size -= self._getsize(value)

    @classmethod
    def _getsize(cls, obj_0):
        """Recursively iterate to sum size of object & members."""
        try:  # Python 2
            zero_depth_bases = (basestring, Number, xrange, bytearray)
            iteritems = 'iteritems'
        except NameError:  # Python 3
            zero_depth_bases = (str, bytes, Number, range, bytearray)
            iteritems = 'items'

        def inner(obj):
            """Recursive get size method does all the real work."""
            obj_id = id(obj)
            _seen_ids = cls._seen_ids
            if obj_id in _seen_ids:
                return 0
            _seen_ids.add(obj_id)
            size = sys.getsizeof(obj)
            if isinstance(obj, zero_depth_bases):
                pass  # bypass remaining control flow and return
            elif isinstance(obj, (tuple, list, Set, deque)):
                size += sum(inner(i) for i in obj)
            elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
                size += sum(inner(k) + inner(v)
                            for k, v in getattr(obj, iteritems)())
            # Check for custom object instances - may subclass above too
            if hasattr(obj, '__dict__'):
                size += inner(vars(obj))
            if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
                size += sum(inner(getattr(obj, s))
                            for s in obj.__slots__ if hasattr(obj, s))
            return size
        return inner(obj_0)


def trans_science_themes(obj):
    """Render the science theme from a proposal."""
    return [SearchRender.render_science_theme(
        SearchRender.get_obj_by_id('proposals', obj['proposal'])
    )]


def trans_proposals(obj):
    """Render the proposals for a transaction."""
    return [SearchRender.render(
        'proposals',
        SearchRender.get_obj_by_id('proposals', obj['proposal'])
    )]


def trans_inst_groups(obj):
    """Render the instrument groups for a transaction."""
    return SearchRender.get_groups_from_instrument(obj['instrument'])


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

    obj_cache = LimitedSizeDict(size_limit=CACHE_SIZE)
    render_data = {
        'instruments': {
            'display_name': text_type('{display_name}'),
            'long_name': text_type('{name}')
        },
        'institutions': {
            'display_name': text_type('{name}')
        },
        'users': {
            'display_name': text_type('{first_name}, {last_name} {middle_initial}')
        },
        'proposals': {
            'display_name': text_type('{title}'),
            'long_name': text_type(''),
            'abstract': text_type('{abstract}'),
            'title': text_type('{title}'),
        },
        'groups': {
            'display_name': text_type('{name}')
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

    global_get_args = {
        'recursion_depth': '0',
        'recursion_limit': '1'
    }

    @classmethod
    def merge_get_args(cls, get_args):
        """Change a hash of get args and global get args into string for url."""
        get_args.update(cls.global_get_args)
        get_list = ['{}={}'.format(key, val) for key, val in get_args.items()]
        return '&'.join(get_list)

    @classmethod
    def get_obj_by_id(cls, obj, obj_id):
        """Get the user from metadata and put it in cache."""
        key = text_type('{}_{}').format(obj, obj_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val
        url = '{base_url}/{obj}?'+cls.merge_get_args({'_id': '{obj_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                obj=obj,
                obj_id=obj_id
            )
        )
        cls.obj_cache[key] = resp.json()[0]
        return cls.obj_cache[key]

    @classmethod
    def get_institutions_from_user(cls, user_id):
        """Get an institution list based on user id."""
        key = text_type('inst_by_user_{}').format(user_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/institution_person?' + \
            cls.merge_get_args({'person_id': '{user_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                user_id=user_id
            )
        )
        ret = []
        for inst_id in [obj['institution_id'] for obj in resp.json()]:
            ret.append(cls.render('institutions',
                                  cls.get_obj_by_id('institutions', inst_id)))
        cls.obj_cache[key] = ret
        return ret

    @classmethod
    def get_groups_from_instrument(cls, inst_id):
        """Get the list of groups from an instrument."""
        key = text_type('grp_by_inst_{}').format(inst_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/instrument_group?' + \
            cls.merge_get_args({'instrument_id': '{inst_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        ret = []
        for grp_id in [obj['group_id'] for obj in resp.json()]:
            ret.append(cls.render(
                'groups', cls.get_obj_by_id('groups', grp_id)))
        cls.obj_cache[key] = ret
        return ret

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_institutions(cls, inst_id):
        """Get a list of transactions from an institution."""
        key = text_type('trans_by_instit_{}').format(inst_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/institution_person?' + \
            cls.merge_get_args({'institution_id': '{inst_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        ret = []
        for user_id in [obj['person_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_users(user_id))
        cls.obj_cache[key] = ret
        return ret
    # pylint: enable=invalid-name

    @classmethod
    def get_transactions_from_users(cls, user_id):
        """Get a list of transactions for a user."""
        key = text_type('trans_by_user_{}').format(user_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/transactions?' + \
            cls.merge_get_args({'submitter': '{user_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                user_id=user_id
            )
        )
        cls.obj_cache[key] = ['transactions_{}'.format(
            obj['_id']) for obj in resp.json()]
        return cls.obj_cache[key]

    @classmethod
    def get_transactions_from_proposals(cls, prop_id):
        """Get a list of transactions for a proposal."""
        key = text_type('trans_by_prop_{}').format(prop_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/transactions?' + \
            cls.merge_get_args({'proposal': '{prop_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                prop_id=prop_id
            )
        )
        cls.obj_cache[key] = ['transactions_{}'.format(
            obj['_id']) for obj in resp.json()]
        return cls.obj_cache[key]

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_instruments(cls, inst_id):
        """Get a list of transactions for a instrument."""
        key = text_type('trans_by_inst_{}').format(inst_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/transactions?' + \
            cls.merge_get_args({'instrument': '{inst_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                inst_id=inst_id
            )
        )
        cls.obj_cache[key] = ['transactions_{}'.format(
            obj['_id']) for obj in resp.json()]
        return cls.obj_cache[key]
    # pylint: enable=invalid-name

    @classmethod
    def get_transactions_from_groups(cls, group_id):
        """Get a list of instruments for a group."""
        key = text_type('trans_by_group_{}').format(group_id)
        val = cls.obj_cache.get(key, None)
        if val is not None:  # pragma: no cover
            return val

        url = '{base_url}/instrument_group?' + \
            cls.merge_get_args({'group_id': '{group_id}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                group_id=group_id
            )
        )
        ret = []
        for inst_id in [obj['instrument_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_instruments(inst_id))
        cls.obj_cache[key] = ret
        return ret

    # pylint: disable=invalid-name
    @classmethod
    def get_transactions_from_science_theme(cls, science_theme):
        """Get a list of transactions for a science theme."""
        key = text_type('trans_by_sci_{}').format(science_theme)
        val = cls.obj_cache.get(key, None)
        if val is not None:
            return val

        url = '{base_url}/proposals?' + \
            cls.merge_get_args({'science_theme': '{science_theme}'})
        resp = requests.get(
            text_type(url).format(
                base_url=METADATA_ENDPOINT,
                science_theme=science_theme
            )
        )
        ret = []
        for prop_id in [obj['_id'] for obj in resp.json()]:
            ret.extend(cls.get_transactions_from_proposals(prop_id))
        cls.obj_cache[key] = ret
        return ret
    # pylint: enable=invalid-name

    @classmethod
    def generate(cls, obj_cls, objs, trans_ids=False):
        """generate the institution object."""
        for obj in objs:
            yield {
                '_op_type': 'update',
                '_index': ELASTIC_INDEX,
                '_type': obj_cls,
                '_id': text_type('{}_{}').format(obj_cls, obj['_id']),
                'doc': cls.render(obj_cls, obj, trans_ids),
                'doc_as_upsert': True
            }
            if obj_cls == 'proposals':
                yield {
                    '_op_type': 'update',
                    '_index': ELASTIC_INDEX,
                    '_type': 'science_theme',
                    '_id': text_type('science_theme_{}').format(obj['science_theme']),
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
