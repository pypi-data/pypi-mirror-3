#!/usr/bin/env python

import os
import re

from unittest import TestLoader
from pkg_resources import resource_exists
from pkg_resources import resource_listdir
from setuptools import setup
from setuptools import find_packages

VERSION = '2.8.0-rc'

LONG_DESC = """\
This is a simple, easily extendible rpc library that provides several useful
tools for creating and publishing web services in python.  This package
features on-demand wsdl generation for the published services, a
wsgi-compliant web application, support for complex class structures, binary
attachments, and a simple framework for creating additional serialization
mechanisms.

This project uses lxml as it's XML API, providing full namespace support.
"""

try:
    os.stat('CHANGELOG.rst')
    LONG_DESC += open('CHANGELOG.rst', 'r').read()
except OSError:
    pass


SHORT_DESC="A transport and architecture agnostic rpc (de)serialization " \
           "library that focuses on making small, rpc-oriented messaging work."


setup(
    name='rpclib',
    packages=find_packages(),

    version=VERSION,
    description=SHORT_DESC,
    long_description=LONG_DESC,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords=('soap', 'wsdl', 'wsgi', 'zeromq', 'rest', 'rpc', 'json', 'http'),
    author='Burak Arslan',
    author_email='burak+rpclib@arskom.com.tr',
    maintainer='Burak Arslan',
    maintainer_email='burak+rpclib@arskom.com.tr',
    url='http://github.com/arskom/rpclib',
    license='LGPL-2.1',
    zip_safe=False,
    install_requires=['spyne'],
)
