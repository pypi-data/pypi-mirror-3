#!/usr/bin/env python

import sys
from distutils.core import setup
from setuptools import setup, find_packages

install_requires=[]
if sys.version_info < (2,7):
    install_requires=['argparse>=1.1']

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Internet',
    'Topic :: System :: Archiving :: Backup',
    'Topic :: System :: Distributed Computing',
]

setup(
    name='scatterbytes',
    version='0.8.8',
    description='Library and CLI for accessing the ScatterBytes Network',
    author='Randall Smith',
    author_email='randall@scatterbytes.net',
    url='https://www.scatterbytes.net',
    packages=find_packages(),
    license="BSD License",
    install_requires=install_requires,
    tests_require=['nose>=0.11'],
    scripts=['scripts/sbnet'],
    classifiers = classifiers,
)
