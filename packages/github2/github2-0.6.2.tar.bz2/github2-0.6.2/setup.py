#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009-2012 Ask Solem <askh@modwheel.net>
#                         Cody Soyland <codysoyland@gmail.com>
#                         Donald von Stufft <donald@xenofox.com>
#                         James Rowe <jnrowe@gmail.com>
#                         Maximillian Dornseif <m.dornseif@hudora.de>
#                         Michael Basnight <mbasnight@gmail.com>
#
# This file is part of python-github2, and is made available under the 3-clause
# BSD license.  See LICENSE for the full details.

import codecs
import sys

from setuptools import setup, find_packages

import github2


install_requires = ['httplib2 >= 0.7.0', ]

# simplejson is included in the standard library since Python 2.6 as json
if sys.version_info < (2, 5):
    # 2.1 drops support for 2.4
    install_requires.append('simplejson >= 2.0.9, < 2.1')
elif sys.version_info[:2] < (2, 6):
    install_requires.append('simplejson >= 2.0.9')

# dateutil supports python 2.x in dateutil-1, python 3.x in dateutil-2.0 and
# python 2.6+ in dateutil-2.1.  Exciting…
if sys.version_info[:2] <= (2, 5):
    install_requires.append('python-dateutil < 2.0')
elif sys.version_info < (3, ):
    install_requires.append('python-dateutil < 2.0, >= 2.1')
else:
    install_requires.append('python-dateutil > 2.0')

long_description = (codecs.open('README.rst', "r", "utf-8").read()
    + "\n" + codecs.open('NEWS.rst', "r", "utf-8").read())

setup(
    name='github2',
    version=github2.__version__,
    description=github2.__doc__,
    long_description=long_description,
    author=github2.__author__,
    author_email=github2.__contact__,
    url=github2.__homepage__,
    license='BSD',
    keywords="git github api",
    platforms=["any"],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={'': ['*.crt', ], },
    entry_points={
        'console_scripts': [
            'github_manage_collaborators = github2.bin.manage_collaborators:main',
            'github_search_repos = github2.bin.search_repos:main',
        ],
    },
    install_requires=install_requires,
    zip_safe=True,
    test_suite="nose.collector",
    tests_require=['nose'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
    ],
)
