import requests
import os
import flyingsphinx

class API(object):
  URI_BASE   = 'https://flying-sphinx.com/api/my/app/'
  API_ACCEPT = 'application/vnd.flying-sphinx-v3+json'

  def __init__(self, identifier = None, api_key = None):
    self.identifier = identifier or os.environ['FLYING_SPHINX_IDENTIFIER']
    self.api_key    = api_key    or os.environ['FLYING_SPHINX_API_KEY']

  def get(self, path, body={}):
    requests.get(API.URI_BASE + path, body, self._headers())

  def post(self, path, body={}):
    requests.post(API.URI_BASE + path, body, self._headers())

  def put(self, path, body={}):
    requests.put(API.URI_BASE + path, body, self._headers())

  def _headers(self):
    return {
      'Accept':                  API.API_ACCEPT,
      'X-Flying-Sphinx-Token':   ('%s:%s' % (self.identifier, self.api_key)),
      'X-Flying-Sphinx-Version': ('%s+python' % flyingsphinx.__version__)
    }
