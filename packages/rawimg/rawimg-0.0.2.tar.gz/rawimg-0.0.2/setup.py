#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

NAME = 'rawimg'
VERSION = '0.0.2'

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    sys.exit()

setup(
    name=NAME,
    version=VERSION,
    description='',
    long_description=open('README.rst').read(),
    author='SATO Naoya',
    author_email='s@tonaoya.com',
    url='',
    packages=['rawimg', ],
    install_requires=[
        'PIL>=1.1.7',
    ],
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
#        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points={
        'console_scripts': [
            'rawimg = rawimg.cli:main',
        ],
    }
)
