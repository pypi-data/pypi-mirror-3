"""
flyingsphinx
~~~~~~~~~~~~

:copyright: (c) 2012 by Pat Allan
:license: MIT, see LICENCE for more details.
"""

__title__     = 'flyingsphinx'
__version__   = '0.0.6'
__author__    = 'Pat Allan'
__license__   = 'MIT'
__copyright__ = 'Copyright 2012 Pat Allan'

from .api           import API
from .configuration import Configuration
from .sphinx        import Sphinx

def sphinx():
  return Sphinx(API())

def version():
  return __version__