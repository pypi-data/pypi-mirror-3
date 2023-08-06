class Configuration(object):
  def __init__(self, api):
    self.api = api

  def upload(self, configuration):
    self.api.put('/', {'configuration': configuration})

  def upload_from_file(self, path):
    file     = open(path)
    contents = file.read()
    self.upload(contents)
