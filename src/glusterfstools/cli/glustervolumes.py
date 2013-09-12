# -*- coding: utf-8 -*-
"""
    glusterfstools.cli.glustervolumes

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import json
import sys

from glusterfstools import volumes

PROG_DESCRIPTION = """
GlusterFS Volumes summary
"""


class COLORS:
    RED = "\033[31m"
    GREEN = "\033[32m"
    NOCOLOR = "\033[0m"


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


def _color_txt(txt, color):
    return "%s%s%s" % (getattr(COLORS, color, COLORS.NOCOLOR),
                       txt,
                       COLORS.NOCOLOR)


def _print_header(args):
    op = [ColumnFormat.UUID % 'UUID',
          ColumnFormat.NAME % 'NAME',
          ColumnFormat.STATUS % 'STATUS',
          ColumnFormat.TYPE % 'TYPE',
          ColumnFormat.NUM_BRICKS % 'NUM_BRICKS']

    if args.show_detail:
        op += [ColumnFormat.TRANSPORT_TYPE % 'TRANSPORT',
               ColumnFormat.REPLICA % 'REPLICA',
               ColumnFormat.DISTRIBUTE % 'DISTRIBUTE',
               ColumnFormat.STRIPE % 'STRIPE']

    header = ' '.join(op)
    sys.stdout.write(header + "\n")
    sys.stdout.write('-'*(len(header)) + "\n")


def _print_vol_row(vol, args):
    color = "GREEN" if vol['status'] == "UP" else "RED"
    op = [ColumnFormat.UUID % vol['uuid'],
          ColumnFormat.NAME % vol['name'],
          _color_txt(ColumnFormat.STATUS % vol['status'], color),
          ColumnFormat.TYPE % vol['type'],
          ColumnFormat.NUM_BRICKS % vol['num_bricks']]

    if args.show_detail:
        op += [ColumnFormat.TRANSPORT_TYPE % vol['transport'],
               ColumnFormat.REPLICA % vol['replica'],
               ColumnFormat.DISTRIBUTE % vol['distribute'],
               ColumnFormat.STRIPE % vol['stripe']]

    sys.stdout.write(' '.join(op) + "\n")


def _display(vols, args):
    _print_header(args)

    for vol in vols:
        _print_vol_row(vol, args)
        if args.show_bricks:
            sys.stdout.write('Bricks:\n---------\n')
            for n, brick in enumerate(vol["bricks"]):
                sys.stdout.write('%s. %s\n' % (n+1, brick))
            sys.stdout.write('\n')
        if args.show_options:
            sys.stdout.write('Options:\n---------\n')
            for opt in enumerate(vol['options']):
                sys.stdout.write('%s: %s\n' % (opt, opts[opt]))
            sys.stdout.write('\n')


def _get_args():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=PROG_DESCRIPTION)
    parser.add_argument('--status', help="Status to filter", type=str,
                        default='')
    parser.add_argument('--json', help="JSON Output", action='store_true')
    parser.add_argument('--name', help="Name to filter", type=str, default='')
    parser.add_argument('--type', help="Type to filter", type=str, default='')
    parser.add_argument('--volumewithbricks', type=str, default='',
                        help="Show GlusterFS volumes with these bricks")
    parser.add_argument('--show-detail', action='store_true',
                        help="Show Replica/distribute/stripe count")
    parser.add_argument('--show-bricks', help="Show bricks",
                        action='store_true')
    parser.add_argument('--show-options', help="Show Volume Options",
                        action='store_true')

    return parser.parse_args()


def main():
    args = _get_args()

    filters = {
        "name": args.name,
        "status": args.status,
        "type": args.type,
        "volumewithbricks": args.volumewithbricks
    }

    try:
        gfvols = volumes.search(filters)
    except volumes.GlusterVolumeInfoFailed:
        sys.stderr.write(_color_txt('Error fetching gluster volumes details\n',
                                    'RED'))
        exit(1)

    if args.json:
        sys.stdout.write(json.dumps(gfvols))
        exit(0)

    if not gfvols:
        exit(0)

    _display(gfvols, args)


if __name__ == '__main__':
    main()
    exit(0)
