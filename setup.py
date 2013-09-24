# -*- coding: utf-8 -*-
"""
    setup.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name = "GlusterFS Tools",
    version = "0.2",
    package_dir = {"": "src"},
    packages = ["glusterfstools", "glusterfstools.cli"],
    include_package_data = True,
    install_requires = ['argparse'],

    entry_points = {
        "console_scripts": [
            "glusterdf = glusterfstools.cli.glusterdf:main",
            "glustervolumes = glusterfstools.cli.glustervolumes:main",
        ]
    },
    platforms = "linux",
    zip_safe=False,
    author = "Aravinda VK",
    author_email = "mail@aravindavk.in",
    description = "GlusterFS Tools",
    license = "BSD",
    keywords = "glusterfs, cli",
    url = "https://github.com/aravindavk/glusterfs-tools",
)
