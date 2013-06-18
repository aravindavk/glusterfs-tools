#!/usr/bin/python

# Copyright (C) 2013, Aravinda VK <mail@aravindavk.in>
#                                  http://aravindavk.in

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import json
import re
import subprocess
import xml.etree.cElementTree as etree


PROG_DESCRIPTION = """
GlusterFS Volumes summary
"""


def exec_cmd(cmd, env=None):
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=env,
                         close_fds=True)

    (out, err) = p.communicate()
    return (p.returncode, out, err)


class GfVolumes:
    def __init__(self):
        self.name_filter = ''
        self.status_filter = ''
        self.type_filter = ''
        self.brick_filter = ''
        self.json = False

    def _get_info(self):
        cmd = ['gluster', 'volume', 'info', '--xml']
        rc, out, err = exec_cmd(cmd)
        if rc == 0:
            return (True, out)
        else:
            return (False, 'Error fetching Volumes details')

    def apply_filter_name(self, field):
        if self.name_filter in ['', 'all'] or \
                field.lower() == self.name_filter.lower().strip() or \
                re.search(self.name_filter, field):
            return True
        else:
            return False

    def apply_filter_status(self, field):
        if self.status_filter in ['', 'all'] or \
                field.lower() == self.status_filter:
            return True
        else:
            return False

    def apply_filter_type(self, field):
        if self.type_filter in ['', 'all'] or \
                field.lower() == self.type_filter.lower() or \
                re.search(self.type_filter, field, re.I):
            return True
        else:
            return False

    def apply_filter_brick(self, field):
        if self.brick_filter in ['', 'all'] or \
                field.lower() == self.brick_filter.lower() or \
                re.search(self.brick_filter, field, re.I):
            return True
        else:
            return False

    def _parse_and_apply_filter(self, volume_el):
        value = {}
        value['transport_type'] = ['TCP', 'RDMA']

        value['name'] = volume_el.find('name').text
        value['uuid'] = volume_el.find('id').text
        value['type'] = volume_el.find('typeStr').text
        value['type'] = value['type'].upper().replace('-', '_')
        status = volume_el.find('statusStr').text.upper()
        value["status"] = 'UP' if status == 'STARTED' else 'DOWN'
        value['num_bricks'] = int(volume_el.find('brickCount').text)
        value['distribute'] = int(volume_el.find('distCount').text)
        value['stripe'] = int(volume_el.find('stripeCount').text)
        value['replica'] = int(volume_el.find('replicaCount').text)
        transportType = volume_el.find('transport').text
        if transportType == '0':
            value['transport_type'] = ['TCP']
        elif transportType == '1':
            value['transport_type'] = ['RDMA']

        value['bricks'] = []
        value['options'] = {}
        for b in volume_el.findall('bricks/brick'):
            if not self.apply_filter_brick(b.text):
                return {}
            value['bricks'].append(b.text)

        for o in volume_el.findall('options/option'):
            value['options'][o.find('name').text] = o.find('value').text

        # Include only if user requested filter is satisfied
        if not self.apply_filter_status(value["status"]):
            return {}

        if not self.apply_filter_name(value["name"]):
            return {}

        if not self.apply_filter_type(value["type"]):
            return {}

        return value

    def _parse_info(self):
        ok, info = self._get_info()
        if not ok:
            return (ok, [])

        tree = etree.fromstring(info)
        volumes = []
        for el in tree.findall('volInfo/volumes/volume'):
            value = self._parse_and_apply_filter(el)
            if value:
                volumes.append(value)
        return (ok, volumes)

    def get(self, name='', status='', format_json=False,
            volume_type='', brick=''):
        self.name_filter = name
        self.status_filter = status.lower().strip()
        self.type_filter = volume_type.strip()
        self.brick_filter = brick
        self.json = format_json

        ok, volumes = self._parse_info()
        if self.json:
            return (ok, json.dumps(volumes))
        else:
            return (ok, volumes)


def _get_args():
    # Argument parser description and parameters
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=PROG_DESCRIPTION)
    parser.add_argument('--status',
                        help="Status to filter",
                        type=str,
                        default='')
    parser.add_argument('--json',
                        help="JSON Output",
                        action='store_true')
    parser.add_argument('--name',
                        help="Name to filter",
                        type=str,
                        default='')
    parser.add_argument('--type',
                        help="Type to filter",
                        type=str,
                        default='')
    parser.add_argument('--brick',
                        help="Brick to filter",
                        type=str,
                        default='')
    parser.add_argument('--show-detail',
                        help="Show Replica/distribute/stripe count",
                        action='store_true')
    parser.add_argument('--show-bricks',
                        help="Show bricks",
                        action='store_true')
    parser.add_argument('--show-options',
                        help="Show Volume Options",
                        action='store_true')

    return parser.parse_args()


class ColumnFormat:
    UUID = '%36s'
    NAME = '%20s'
    STATUS = '%6s'
    TYPE = '%15s'
    NUM_BRICKS = '%10s'
    TRANSPORT_TYPE = '%10s'
    REPLICA = '%7s'
    DISTRIBUTE = '%10s'
    STRIPE = '%6s'


def _print_header(extra=False):
    op = [ColumnFormat.UUID % 'UUID',
          ColumnFormat.NAME % 'NAME',
          ColumnFormat.STATUS % 'STATUS',
          ColumnFormat.TYPE % 'TYPE',
          ColumnFormat.NUM_BRICKS % 'NUM_BRICKS']

    if extra:
        op += [ColumnFormat.TRANSPORT_TYPE % 'TRANSPORT',
               ColumnFormat.REPLICA % 'REPLICA',
               ColumnFormat.DISTRIBUTE % 'DISTRIBUTE',
               ColumnFormat.STRIPE % 'STRIPE']

    header = ' '.join(op)
    print (header)
    print ('-'*(len(header)))


def _print_vol_row(vol, extra=False):
    op = [ColumnFormat.UUID % vol['uuid'],
          ColumnFormat.NAME % vol['name'],
          ColumnFormat.STATUS % vol['status'],
          ColumnFormat.TYPE % vol['type'],
          ColumnFormat.NUM_BRICKS % vol['num_bricks']]

    if extra:
        op += [ColumnFormat.TRANSPORT_TYPE % ','.join(vol['transport_type']),
               ColumnFormat.REPLICA % vol['replica'],
               ColumnFormat.DISTRIBUTE % vol['distribute'],
               ColumnFormat.STRIPE % vol['stripe']]

    print (' '.join(op))


def _print_bricks(bricks):
    print ('Bricks:\n---------')
    for n, brick in enumerate(bricks):
        print ('%s. %s' % (n+1, brick))
    print ('\n')


def _print_options(opts):
    print ('Options:\n---------')
    for opt in enumerate(opts):
        print ('%s: %s' % (opt, opts[opt]))
    print ('\n')


def main():
    args = _get_args()
    gfvols = GfVolumes()
    ok, volumes = gfvols.get(name=args.name,
                             status=args.status,
                             volume_type=args.type,
                             brick=args.brick,
                             format_json=args.json)

    if not ok:
        print ('Error fetching gluster volumes details')
        exit(1)

    if args.json:
        print (volumes)
        exit(0)

    # CLI Output
    if not volumes:
        return

    _print_header(args.show_detail)

    for vol in volumes:
        _print_vol_row(vol, args.show_detail)
        if args.show_bricks:
            _print_bricks(vol['bricks'])

        if args.show_options:
            _print_options(vol['options'])


if __name__ == '__main__':
    main()
    exit(0)
