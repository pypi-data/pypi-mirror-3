#!/usr/bin/env python

import sys

if not hasattr(sys, 'hexversion') or sys.hexversion < 0x02060000:
    print "OfArchiver requires Python 2.6 or newer"
    sys.exit(1)

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name = 'ofarchiver',
    version = '0.43',
    packages = ['ofarchiver',],
    data_files = [
      ('config', ['cfg/ofarchiver.ini']),
    ],

    entry_points = {
        'console_scripts': [
            'ofarchiver = ofarchiver:main',
        ],
    },

    install_requires = ['chardet', 'configobj', 'HTML.py', 'mysql-python',],

    author = 'John A. Barbuto',
    author_email = 'jbarbuto@egnyte.com',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Chat',
        'Topic :: System :: Archiving',
    ],
    description = 'An HTML archive generator for chat rooms on an Openfire instant messaging server.',
    long_description = open('README.rst').read(),
    license = 'MIT',
    platforms = ['POSIX',],
    keywords = ['archiving', 'chat', 'html', 'openfire',],
    url = 'http://github.com/egnyte/ofarchiver',
)
