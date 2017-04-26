# -*- coding: utf-8 -*-
"""
    glusterfstools.cli.glusterdf

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter, SUPPRESS
import json
import re
import sys

from glusterfstools import volumes, utils
from gluster.gfapi import Volume
from gluster.cli import volume


PROG_DESCRIPTION = """
Show information about the GlusterFS volumes
"""


FIELDS = {
    "volume": {"title": "Volume", "format": "%25s"},
    "itotal": {"title": "Inodes", "format": "%20s"},
    "iused": {"title": "IUsed", "format": "%20s"},
    "iavail": {"title": "IFree", "format": "%20s"},
    "ipcent": {"title": "IUse%", "format": "%10s"},
    "size": {"title": "Size", "format": "%20s"},
    "used": {"title": "Used", "format": "%20s"},
    "avail": {"title": "Avail", "format": "%20s"},
    "pcent": {"title": "Use%", "format": "%10s"},
    "status": {"title": "Status", "format": "%10s"},
    "type": {"title": "Type", "format": "%20s"},
    "num_bricks": {"title": "Bricks", "format": "%10s"}
}


SYMBOLS = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
HUMAN_READABLE_REQUIRED_FIELDS = ('size', 'avail', 'itotal', 'used', 'iused')


def _format_bytes(num, args):
    if args.human_readable or args.human_readable_1000:
        for s in reversed(SYMBOLS):
            power = SYMBOLS.index(s)+1
            if num >= args.hr_block_size**power:
                value = float(num) / (args.hr_block_size**power)
                return '%.1f%s' % (value, s)

    # if size less than 1024 or human readable not required
    return '%s' % (num/args.block_size_number)


def _format_output(data, args, header=False):
    fields = args.fields.split(",")
    for f in fields:
        f = f.strip()
        value = FIELDS[f]["title"] if header else data[f]

        if not header and f == "status":
            color = "GREEN" if value == "Started" else "RED"
            value = utils.color_txt(FIELDS[f]["format"] % value, color)
        else:
            value = FIELDS[f]["format"] % value

        sys.stdout.write(value)
        sys.stdout.write(" ")

    sys.stdout.write("\n")


def _statvfs_data(vol):
    gvol = Volume("localhost", vol["name"])
    gvol.mount()
    statvfs_data = gvol.statvfs("/")
    gvol.umount()

    data = {
        "volume": vol["name"],
        "status": vol["status"],
        "type": vol["type"],
        "num_bricks": vol["num_bricks"],
        "size": ((statvfs_data.f_blocks -
                  (statvfs_data.f_bfree - statvfs_data.f_bavail)) *
                 statvfs_data.f_bsize),
        "avail": statvfs_data.f_bavail * statvfs_data.f_bsize,
        "itotal": (statvfs_data.f_files -
                   (statvfs_data.f_ffree - statvfs_data.f_favail)),
        "iavail": statvfs_data.f_favail
    }

    data["used"] = data["size"] - data["avail"]
    data["iused"] = data["itotal"] - data["iavail"]
    data["pcent"] = 0
    data["ipcent"] = 0

    if data["size"] > 0:
        data["pcent"] = data["used"] * 100 / data["size"]

    if data["itotal"] > 0:
        data["ipcent"] = data["iused"] * 100 / data["itotal"]

    data['pcent'] = "%s%%" % data['pcent']
    data['ipcent'] = "%s%%" % data['ipcent']

    return data


def _display(gvols, args):
    if gvols and not args.json:
        _format_output({}, args, header=True)

    vols_data = []
    for vol in gvols:
        data = {
            "volume": vol["name"],
            "status": vol["status"],
            "type": vol["type"],
            "num_bricks": vol["num_bricks"],
            "size": "-",
            "avail": "-",
            "itotal": "-",
            "iavail": "-",
            "used": "-",
            "pcent": "-",
            "iused": "-",
            "ipcent": "-"
        }

        if vol["status"] == "Started":
            data = _statvfs_data(vol)

        for f in HUMAN_READABLE_REQUIRED_FIELDS:
            if data["status"] == "Started":
                data[f] = _format_bytes(data[f], args)

        if args.json:
            vols_data.append(data)
        else:
            _format_output(data, args, header=False)

    if args.json:
        sys.stdout.write(json.dumps(vols_data))
        exit(0)


def _get_args():
    # Argument parser description and parameters
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=PROG_DESCRIPTION, add_help=False)

    parser.add_argument('-B', '--block-size',
                        help="scale sizes by SIZE before printing them.  \
                        E.g., '-BM' prints sizes in units of 1,048,576 bytes. \
                        See SIZE format below.",
                        type=str, default='')
    parser.add_argument('-k', help="like --block-size=1K",
                        action='store_true', dest="onek")
    parser.add_argument('-h', '--human-readable', action='store_true',
                        help="print sizes in human readable format \
                        (e.g., 1K 2M 2G)")
    parser.add_argument('-H', '--si', action='store_true',
                        dest='human_readable_1000',
                        help="likewise, but use powers of 1000 not 1024")
    # parser.add_argument('--total',
    #                     help="produce a grand total", action='store_true')
    parser.add_argument('-i', '--inodes', action='store_true',
                        help="list inode information instead of block usage")
    parser.add_argument("--help", action="help",
                        help="show this help message and exit")
    parser.add_argument('--json', help="JSON Output", action='store_true')
    parser.add_argument('name', help="Volume Name",
                        type=str, nargs="?")
    # Derived values
    parser.add_argument('--block-size-number', help=SUPPRESS, default=1)
    parser.add_argument('--hr-block-size', help=SUPPRESS, default=1024)
    parser.add_argument('--fields', help=SUPPRESS,
                        default="volume,type,num_bricks,status,size,used,\
                        avail,pcent")

    return parser.parse_args()


def _get_block_size(args):
    if args.block_size == '':
        return 1

    m = re.search("(\d+)?(K|M|G|T|P|E|Z|Y)?", args.block_size)
    if m:
        numeric = 1 if m.group(1) is None else int(m.group(1))
        suffix = 'B' if m.group(2) is None else m.group(2)
        return (numeric *
                (1024**(SYMBOLS.index(suffix)+1)
                 if suffix in SYMBOLS
                 else 1))
    else:
        sys.stdout.write("Unknown value for -B\n")
        exit(1)


def main():
    args = _get_args()

    try:
        gvols = volume.info(args.name)
    except volumes.GlusterVolumeInfoFailed:
        msg = 'Error fetching gluster volumes details\n'
        sys.stderr.write(utils.color_txt(msg,
                                         'RED'))
        exit(1)

    if args.onek:
        args.block_size = 'K'

    if args.block_size != '':
        args.human_readable = False
        args.human_readable_1000 = False

    args.hr_block_size = 1000 if args.human_readable_1000 else 1024
    args.block_size_number = _get_block_size(args)

    if args.inodes:
        args.fields = "volume,type,num_bricks,status,itotal,\
        iused,iavail,ipcent"

    _display(gvols, args)


if __name__ == '__main__':
    main()
    exit(0)
