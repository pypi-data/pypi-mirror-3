"""Setuptools setup file"""

import sys
import os
import logging

from setuptools import setup

# Ridiculous as it may seem, we need to import multiprocessing and logging here
# in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except:
    pass


def get_description():
    f = open("README.rst", 'r')
    content = f.read()
    f.close()
    return content.split('.. split here')[-1]

requires = [
    'mattd.core',
]

setup(
    name='mattd.plugins.mplayer',
    version='0.0.6',
    description="MPlayer plugin for Matt Daemon",
    long_description=get_description(),
    install_requires=requires,
    url="http://mattd.rtfd.org/",
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    license='AGPLv3+',
    packages=['mattd', 'mattd.plugins', 'mattd.plugins.mplayer'],
    namespace_packages=['mattd', 'mattd.plugins'],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [mattd.plugins]
    mplayer = mattd.plugins.mplayer:MPlayerPlugin
    """,
)
