import urllib3

import six
import gssapi
import requests
from requests_gssapi import HTTPSPNEGOAuth, REQUIRED

from .rest import RESTClientObject


def request(self, method, url, query_params=None, headers=None,
                body=None, post_params=None, _preload_content=True,
                _request_timeout=None):
  """Patch fucntion to use requests + gss integration instead of urllib3"""
  if query_params:
    url += '?' + urlencode(query_params)
  name = gssapi.Name('admin@EXAMPLE.TEST', gssapi.NameType.kerberos_principal)
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

  return urllib3.response.HTTPResponse(
    body=r.text,
    headers=r.headers,
    status=r.status_code,
    version='1.1',
    reason=r.reason)


def patch_all():
  """Patches ResClientObject.request method"""
  global RESTClientObject
  RESTClientObject.request = request
