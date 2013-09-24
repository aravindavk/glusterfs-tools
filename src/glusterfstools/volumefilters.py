# -*- coding: utf-8 -*-
"""
    glusterfstools.volumefilters

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from functools import wraps
import re

_volume_filters = {}


def filter(name):
    def filter_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            return f(*args, **kwds)

        global _volume_filters
        _volume_filters[name] = wrapper
        return wrapper
    return filter_decorator


@filter("name")
def name_filter(vols, value):
    def is_match(vol, value):
        if value in ['', 'all'] or \
           vol["name"].lower() == value.lower().strip() or \
           re.search(value, vol["name"]):
            return True
        else:
            return False

    return [v for v in vols if is_match(v, value)]


@filter("status")
def status_filter(vols, value):
    def is_match(vol, value):
        if value in ['', 'all'] or \
           vol["status"].lower() == value.lower().strip():
            return True
        else:
            return False

    return [v for v in vols if is_match(v, value)]


@filter("type")
def type_filter(vols, value):
    def is_match(vol, value):
        if value in ['', 'all'] or \
           vol["type"].lower() == value.lower() or \
           re.search(value, vol["type"], re.I):
            return True
        else:
            return False

    return [v for v in vols if is_match(v, value)]


@filter("volumewithbrick")
def volumewithbrick_filter(vols, value):
    def is_match(vol, value):
        for brick in vol["bricks"]:
            if value in ['', 'all'] or \
               brick.lower() == value.lower() or \
               re.search(value, brick, re.I):
                return True

        # If no single brick matching the query
        return False

    return [v for v in vols if is_match(v, value)]


def get():
    return _volume_filters
