# -*- coding: utf-8 -*-
"""
    glusterfstools.utils

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""


class COLORS:
    RED = "\033[31m"
    GREEN = "\033[32m"
    NOCOLOR = "\033[0m"


def color_txt(txt, color):
    return "%s%s%s" % (getattr(COLORS, color, COLORS.NOCOLOR),
                       txt,
                       COLORS.NOCOLOR)
