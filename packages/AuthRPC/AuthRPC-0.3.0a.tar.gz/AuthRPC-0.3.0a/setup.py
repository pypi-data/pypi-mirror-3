#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages
import platform

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: OS Independent',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Internet :: WWW/HTTP :: WSGI']

extra = {}
if platform.python_version().startswith('3'):
    extra['use_2to3'] = True

setup(name             = 'AuthRPC',
      version          = '0.3.0a',
      packages         = find_packages(),
      install_requires = 'WebOb>=1.2b3',
      author           = 'Ben Croston',
      author_email     = 'ben@croston.org',
      description      = 'A JSONRPC-like client and server with additions to enable authenticated requests',
      long_description = open('README.txt').read() + open('CHANGELOG.txt').read(),
      license          = 'MIT',
      keywords         = 'json, rpc, wsgi, auth',
      url              = 'http://www.wyre-it.co.uk/authrpc/',
      classifiers      = classifiers,
      platforms        = ['Any'],
      test_suite       = 'AuthRPC.tests.suite',
      **extra)

