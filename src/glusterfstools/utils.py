# -*- coding: utf-8 -*-
"""
    glusterfstools.utils

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

import subprocess


def exec_cmd(cmd, env=None):
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=env,
                         close_fds=True)

    (out, err) = p.communicate()
    return (p.returncode, out, err)
