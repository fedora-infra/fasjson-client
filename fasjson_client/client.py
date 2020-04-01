import errno
from urllib.parse import urlparse

import yaml
import requests
from requests_gssapi import HTTPSPNEGOAuth
from bravado import requests_client
from bravado.client import SwaggerClient
import gssapi
from swagger_spec_validator.common import SwaggerValidationError

from . import errors


class HttpClient(requests_client.RequestsClient):
  """
  HttpClient class used in SwaggerClient for gssapi authentication.
  """

  def __init__(self, principal, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.principal = principal

  def authenticated_request(self, request_params):
    """
    Retrieves an authentication token from kerberos
    and adds it in the http header request.
    """
    name = gssapi.Name(self.principal, gssapi.NameType.kerberos_principal)
    try:
      creds = gssapi.Credentials(name=name, usage="initiate")
    except gssapi.raw.misc.GSSError as e:
      data = {
        "trace": repr(e.gen_message),
        "codes": {
          "maj": e.maj_code,
          "min": e.min_code,
          "routine": e.routine_code,
          "supplementary_code": e.supplementary_code,
        },
      }
      raise errors.ClientError(
        "schema validation failed", errno.EPROTO, data=data
      )

    request_params["auth"] = HTTPSPNEGOAuth(creds=creds)

    return super().authenticated_request(request_params)


class Client:
  """
  FasJsonClient client class that builds API methods based on openapi specs.
  """

  def __init__(self, spec, principal):
    self.principal = principal
    self.http_client = HttpClient(principal)
    try:
      self._api = SwaggerClient.from_spec(
        spec,
        http_client=self.http_client,
        config={"disable_fallback_results": True},
      )
    except SwaggerValidationError:
      raise errors.ClientError("schema validation failed", errno.EPROTO)

  @classmethod
  def from_url(cls, spec_url, base_url=None, principal=None):
    """
    Builds a client object from a remote spec file definition.
    """
    try:
      res = requests.get(spec_url)
    except requests.exceptions.RequestException as e:
      data = {
        "trace": e.args[0] if len(e.args) > 0 else repr(e),
      }
      if e.request:
        data["request"] = {"url": e.request.url, "method": "GET"}
      raise errors.ClientError(
        "error loading remote spec data", errno.ECONNABORTED, data=data
      )

    if not res.ok:
      data = {"url": res.url, "method": "GET", "status_code": res.status_code}
      raise errors.ClientError(
        "error loading remote spec data", errno.ECONNABORTED, data=data
      )

    try:
      data = yaml.load(res.text, Loader=yaml.SafeLoader)
    except yaml.parser.ParserError:
      raise errors.ClientError("remote data validation failed", errno.EPROTO)

    return cls.from_spec(data, base_url=base_url, principal=principal)

  @classmethod
  def from_spec(cls, spec_data, base_url=None, principal=None):
    """
    Builds a client object from a spec definition string.
    """
    if base_url:
      parsed = urlparse(base_url)
      if not parsed.netloc or not parsed.scheme:
        data = {"base_url": base_url}
        raise errors.ClientError(
          f"unable to parse base_url: {base_url}", errno.EPROTO, data=data
        )

      spec_data["host"] = parsed.netloc
      spec_data["basePath"] = parsed.path
      spec_data["schemes"] = [parsed.scheme]
    
    return cls(spec_data, principal=principal)

  def __getattr__(self, name):
    return getattr(self._api, name)
