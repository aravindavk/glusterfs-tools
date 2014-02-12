# -*- coding: utf-8 -*-
"""
    glusterfstools.utils

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

import subprocess


class COLORS:
    RED = "\033[31m"
    GREEN = "\033[32m"
    NOCOLOR = "\033[0m"


def exec_cmd(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
             stderr=subprocess.PIPE, env=None, close_fds=True):
    p = subprocess.Popen(cmd,
                         stdin=stdin,
                         stdout=stdout,
                         stderr=stderr,
                         env=env,
                         close_fds=close_fds)

    (out, err) = p.communicate()
    return (p.returncode, out, err)


def color_txt(txt, color):
    return "%s%s%s" % (getattr(COLORS, color, COLORS.NOCOLOR),
                       txt,
                       COLORS.NOCOLOR)
