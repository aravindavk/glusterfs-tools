# -*- coding: utf-8 -*-
"""
    glusterfstools.volumes

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""
from gluster.cli import volume

import volumefilters


_volume_filters = volumefilters.get()


class GlusterVolumeFilterNotFound(Exception):
    pass


def _apply_filters(data, filters):
    for f_name, f_value in filters.iteritems():
        if f_name not in _volume_filters:
            raise GlusterVolumeFilterNotFound(
                "%s filter not available" % f_name)

        data = _volume_filters[f_name](data, f_value)

    return data


def search(filters={}):
    """
    Search volumes based on different filters
    @returns
        {
        'name': STRING,
        'id': UUID,
        'type': STRING,
        'status': STRING,
        'num_bricks': INT,
        'distribute': INT,
        'stripe': INT,
        'replica': INT,
        'transport': STRING,
        'bricks': [{'name': STRING, 'id': UUID},..],
        'options': [{'name': STRING, 'value': STRING},..]
    }
    """
    vols = volume.info()
    return _apply_filters(vols, filters)


def filters():
    return _volume_filters.keys()
