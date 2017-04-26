# -*- coding: utf-8 -*-
"""
    setup.py

    :copyright: (c) 2013, 2014 by Aravinda VK
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup

setup(
    name="Gluster Volume Tools",
    version="0.4",
    package_dir={"": "src"},
    packages=["glusterfstools", "glusterfstools.cli"],
    include_package_data=True,
    install_requires=['argparse', 'pyxattr', 'glustercli', 'gfapi'],
    entry_points={
        "console_scripts": [
            "gluster-df = glusterfstools.cli.glusterdf:main",
            "gluster-volumes = glusterfstools.cli.glustervolumes:main",
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Aravinda VK",
    author_email="mail@aravindavk.in",
    description="Gluster Volume Tools",
    license="MIT",
    keywords="glusterfs, cli, volume",
    url="https://github.com/aravindavk/gluster-volume-tools",
)
