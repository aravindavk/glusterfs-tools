# -*- coding: utf-8 -*-
"""
    glusterfstools.volumes

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

import xml.etree.cElementTree as etree

from utils import exec_cmd
import volumefilters


INFO_CMD = ['gluster', 'volume', 'info']
LIST_CMD = ['gluster', 'volume', 'list']

_volume_filters = volumefilters.get()


class GlusterVolumeInfoFailed(Exception):
    pass


class GlusterBadXmlFormat(Exception):
    pass


class GlusterVolumeFilterNotFound(Exception):
    pass


def _xml_exec(cmd):
    cmd += ["--xml"]
    rc, out, err = exec_cmd(cmd)
    if rc == 0:
        return out
    else:
        raise GlusterVolumeInfoFailed(err)


def _parse_a_vol(volume_el):
    value = {
        'name': volume_el.find('name').text,
        'uuid': volume_el.find('id').text,
        'type': volume_el.find('typeStr').text.upper().replace('-', '_'),
        'status': volume_el.find('statusStr').text.upper(),
        'num_bricks': int(volume_el.find('brickCount').text),
        'distribute': int(volume_el.find('distCount').text),
        'stripe': int(volume_el.find('stripeCount').text),
        'replica': int(volume_el.find('replicaCount').text),
        'transport': volume_el.find('transport').text,
        'bricks': [],
        'options': []
    }

    value["status"] = 'UP' if value["status"] == 'STARTED' else 'DOWN'

    if value['transport'] == '0':
        value['transport'] = 'TCP'
    elif value['transport'] == '1':
        value['transport'] = 'RDMA'
    else:
        value['transport'] = 'TCP,RDMA'

    for b in volume_el.findall('bricks/brick'):
        value['bricks'].append(b.text)

    for o in volume_el.findall('options/option'):
        value['options'].append({"name": o.find('name').text,
                                 "value": o.find('value').text})

    return value


def _parse_vol_info(info):
    tree = etree.fromstring(info)
    volumes = []
    for el in tree.findall('volInfo/volumes/volume'):
        try:
            volumes.append(_parse_a_vol(el))
        except XMLError:
            raise GlusterBadXmlFormat("Error")

    return volumes


def _apply_filters(data, filters):
    for f_name, f_value in filters.iteritems():
        if f_name not in _volume_filters:
            raise GlusterVolumeFilterNotFound(
                "%s filter not available" % f_name)

        data = _volume_filters[f_name](data, f_value)

    return data


def get(name='all'):
    """
    Get all volume info or one volume info
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
    cmd = INFO_CMD if name == "all" else INFO_CMD + [name]
    data = _xml_exec(cmd)
    return _parse_vol_info(data)


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
    data = _xml_exec(INFO_CMD)
    vols = _parse_vol_info(data)
    return _apply_filters(vols, filters)


def filters():
    return _volume_filters.keys()
