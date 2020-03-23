import functools

import urllib3
import six
import gssapi
import requests
from requests_gssapi import HTTPSPNEGOAuth, REQUIRED

from fasjsonclient.openapi_client.rest import RESTClientObject


def request(self, method, url, query_params=None, headers=None,
                body=None, post_params=None, _preload_content=True,
                _request_timeout=None, **kwargs):
  """Patch fucntion to use requests + gssapi integration instead of urllib3"""
  if query_params:
    url += f'?{urlencode(query_params)}'
  principal_name = kwargs.get('principal_name', 'admin@EXAMPLE.TEST')
  name = gssapi.Name(principal_name, gssapi.NameType.kerberos_principal)
  creds = gssapi.Credentials(name=name, usage='initiate')
  gssapi_auth = HTTPSPNEGOAuth(creds=creds)

  timeout = None
  if _request_timeout:
    if isinstance(_request_timeout, (int, ) if six.PY3 else (int, long)):
      timeout = _request_timeout
    elif (isinstance(_request_timeout, tuple) and len(_request_timeout) == 2):
      timeout = _request_timeout[0]

  r = requests.request(method, url,
    headers=headers,
    auth=gssapi_auth,
    data=body,
    timeout=timeout)

def patch_all(principal_name='admin@EXAMPLE.TEST'):
  """Patches ResClientObject.request method"""
  global RESTClientObject
  RESTClientObject.request = functools.partial(request, principal_name=principal_name)
