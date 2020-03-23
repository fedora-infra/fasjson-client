from fasjsonclient.openapi_client import Configuration, ApiClient, DefaultApi
from fasjsonclient.openapi_client.rest import RESTClientObject

from . import patch


class ClientBuilder(object):
  """Class that builder a fasjson openapi rest client object"""
  def __init__(self,
      baseurl='http://fasjson.example.test/fasjson',
      principal_name='admin@EXAMPLE.TEST'):
    self.baseurl = baseurl
    self.principal_name = principal_name

  
  def build(self):
    patch.patch_all(principal_name=self.principal_name)
    config = Configuration(host=self.baseurl)
    api_client = ApiClient(config)
    return DefaultApi(api_client)
