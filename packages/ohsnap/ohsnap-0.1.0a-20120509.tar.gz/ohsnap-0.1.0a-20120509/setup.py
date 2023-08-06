#!/usr/bin/env python

import distribute_setup
distribute_setup.use_setuptools()

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'ohsnap',
    version = '0.1.0',
    author = 'Shawn Siefkas',
    author_email = 'shawn@siefk.as',
    description = 'A tarsnap backup manager',
    license = 'BSD',
    keywords = 'backup tarsnap',
    url = 'http://packages.python.org/ohsnap',
    packages=['ohsnap'],
    long_description=read('README'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires = {
        'pyCLI': ["pycli"],
        'prettytable': ["prettytable"],
    },
    entry_points = {
        'console_scripts': [
            'ohsnap = ohsnap.main:run',
        ],
    }
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
