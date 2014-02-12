#!/usr/bin/python
import subprocess
from glusterfstools import volumes, utils
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

PROG_DESCRIPTION= """

"""

def _get_default_options(lines):
    opts = {}
    for line in lines:
        data = line.split(":", 1)
        if len(data) == 2:
            key, value = data
            if key.strip() == "Option":
                opt_key = value.strip()
                opts[opt_key] = {}
            elif key.strip() == "Default Value":
                opts[opt_key]["value"] = value.strip()
            elif key.strip() == "Description":
                opts[opt_key]["desc"] = value.strip()
    return opts


def _get_args():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=PROG_DESCRIPTION)
    parser.add_argument('--volume', help="Volume Name", type=str,
                        default='')
    parser.add_argument('--json', help="JSON Output", action='store_true')
    parser.add_argument('--option', help="Option to filter(Regex supported)",
                        type=str, default='')
    parser.add_argument('--show-desc', help="Show Description",
                        action='store_true')

    return parser.parse_args()


def main():
    args = _get_args()
    cmd = ["gluster", "volume", "set", "help"]
    rc, out, err = utils.exec_cmd(cmd)

    if rc != 0:
        sys.stderr.write("Failed to get default options\n")
        sys.exit(1)

    opts = _get_default_options(out.split("\n"))

    if args.volume:
        volume_data = volumes.get(args.volume)
        volume_opts = volume_data[0]["options"]
        volume_opts_dict = {}
        for o in volume_opts:
            desc = opts[o["name"]]["desc"] if o["name"] in opts else ""
            volume_opts_dict[o["name"]] = {"value": o["value"], "desc": desc}

        opts.update(volume_opts_dict)


    for k, v in opts.items():
        if args.show_desc:
            sys.stdout.write("%40s %10s %s\n" % (k, v['value'], v["desc"]))
        else:
            sys.stdout.write("%40s %s\n" % (k, v["value"]))

    sys.exit(0)
