# -*- coding: utf-8 -*-
"""
    setup.py

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup

setup(
    name="GlusterFS Tools",
    version="0.3",
    package_dir={"": "src"},
    packages=["glusterfstools", "glusterfstools.cli"],
    include_package_data=True,
    install_requires=['argparse', 'pyxattr'],
    entry_points={
        "console_scripts": [
            "glusterdf = glusterfstools.cli.glusterdf:main",
            "glustervolumes = glusterfstools.cli.glustervolumes:main",
            "glusteroptions = glusterfstools.cli.glusteroptions:main",
            "georepcheckpoint = glusterfstools.cli.georepcheckpoint:main",
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Aravinda VK",
    author_email="mail@aravindavk.in",
    description="GlusterFS Tools",
    license="BSD",
    keywords="glusterfs, cli, geo-replication",
    url="https://github.com/aravindavk/glusterfs-tools",
)
