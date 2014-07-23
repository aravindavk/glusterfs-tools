# -*- coding: utf-8 -*-
"""
    glusterfstools.cli.georepcheckpoint

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime
import json
import struct
import sys
import time
import xattr


DESC = """
Georeplication checkpoint tool:
For a given checkpoint time this tool checks whether
all the files created till that checkpoint is synced or not

Examples:

georepcheckpoint /tmp/gvm 6d93c9ff-6474-4806-bf22-bb023a199f4d
ef94e665-04f6-45a1-af47-a2fc94b238fb "2014-07-22 17:16:05"

georepcheckpoint /tmp/gvm 6d93c9ff-6474-4806-bf22-bb023a199f4d
ef94e665-04f6-45a1-af47-a2fc94b238fb now

georepcheckpoint /tmp/gvm 6d93c9ff-6474-4806-bf22-bb023a199f4d
ef94e665-04f6-45a1-af47-a2fc94b238fb "2014-07-22 17:16:05" --json
"""


def get_args():
    parser = ArgumentParser(description=DESC,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("mount_point", help="Master Volume mount point path")
    parser.add_argument("master_vol_uuid", help="Master Volume UUID")
    parser.add_argument("slave_vol_uuid", help="Slave Volume UUID")
    parser.add_argument("target_time",
                        help="Checkpoint Time in "
                        "%%Y-%%m-%%d %%H:%%M:%%S format or now")
    parser.add_argument("--json", help="JSON output", action="store_true")

    return parser.parse_args()


def human_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def get_target_time(inp):
    if inp.lower() == "now":
        return time.time()
    else:
        t = datetime.strptime(inp, "%Y-%m-%d %H:%M:%S").timetuple()
        return time.mktime(t)


def regular_output(data):
    msg_sfx = "as on %s, last synced time is %s\n" % \
              (data["target_time"], data["last_synced_time"])

    if data["completed"]:
        msg = "Checkpoint completed"
    else:
        msg = "Checkpoint not completed"

    sys.stdout.write("%s %s" % (msg, msg_sfx))


def regular_error(msg):
    sys.stderr.write("Error: %s\n" % msg)


def json_output(data):
    sys.stdout.write(json.dumps({"ok": True, "data": data}))


def json_error(msg):
    sys.stdout.write(json.dumps({"ok": False, "error": msg}))


def main():
    args = get_args()
    target_time = get_target_time(args.target_time)

    xattr_key = "trusted.glusterfs.%s.%s.stime" % \
                (args.master_vol_uuid, args.slave_vol_uuid)
    try:
        stime = struct.unpack("!II", xattr.get(args.mount_point, xattr_key))
        stime = float("%d.%d" % (stime[0], stime[1]))
    except IOError:
        msg = "Unable to read stime xattr from mountpoint, " \
              "please check if volume is mounted and geo-replication " \
              "session is established"
        if args.json:
            json_error(msg)
        else:
            regular_error(msg)

        sys.exit(1)

    data = {"last_synced_time": human_time(stime),
            "target_time": human_time(target_time),
            "completed": False}

    if stime > target_time:
        data["completed"] = True

    if args.json:
        json_output(data)
    else:
        regular_output(data)

    sys.exit(0)


if __name__ == "__main__":
    main()
