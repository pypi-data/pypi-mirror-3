#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

setup(
    name = 'SatchmoBeanstream',
    version = '0.2',
    description = 'Satchmo Beanstream Payment Plugin',
    author = 'Benoit Clennett-Sirois',
    author_email = 'benoit@clennett.com',
    url = 'http://bitbucket.org/benoitcsirois/satchmobeanstream',
    license = 'LGPL',

    install_requires = [
        'pybeanstream',
    ],

    test_suite='nose.collector',
    tests_require = [
        'nose',
        'coverage',
        'pinocchio==0.2',
    ],

    dependency_links = [
        'https://github.com/unpluggd/pinocchio/tarball/0.2#egg=pinocchio-0.2',
    ],

    packages = find_packages(exclude=['tests', ]),
    zip_safe = True,
    include_package_data = True,
    package_data = {'': ['README.txt', 'LICENSE.txt']},

    namespace_packages=['satchmobeanstream', ],

    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
