#! /usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import sys

import procinfo
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    sys.exit()

requires = ['psutil']

setup(
    name='procinfo',
    version=procinfo.__version__,
    description='wrapper around psutil for ease of use',
    long_description=open('README.rst', 'r').read(),
    author='kracekumar',
    author_email='me@kracekumar.com',
    install_requires=requires,
    license=open('LICENSE', 'r').read(),
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Benchmark',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'),
)