#!/usr/bin/env python

import os
import sys

from flyingsphinx import __version__
from setuptools   import setup

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

setup(
  name                 = 'flyingsphinx',
  version              = __version__,
  description          = 'Flying Sphinx Python client',
  long_description     = 'Flying Sphinx API client for Python applications',
  author               = 'Pat Allan',
  author_email         = 'pat@freelancing-gods.com',
  url                  = 'https://github.com/flying-sphinx/flying-sphinx-py',
  packages             = ['flyingsphinx'],
  install_requires     = ['requests'],
  license              = open('LICENCE').read(),
  classifiers          = (
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7'
  )
)
