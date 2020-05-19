import errno

import gssapi
from requests_gssapi import HTTPSPNEGOAuth
from bravado import requests_client

from .errors import ClientError


class GssapiAuthenticator(requests_client.Authenticator):
    """HTTP client class used in SwaggerClient for GSSAPI authentication."""

    def __init__(self, host, principal=None):
        super().__init__(host)
        self.principal = principal

    def apply(self, request):
        request.auth = HTTPSPNEGOAuth(creds=self._get_creds())
        return request

    def _get_creds(self):
        if self.principal is None:
            return None
        name = gssapi.Name(self.principal, gssapi.NameType.kerberos_principal)
        try:
            creds = gssapi.Credentials(name=name, usage="initiate")
        except gssapi.exceptions.GSSError as e:
            raise ClientError("Authentication failed", errno.EPROTO, data={"exc": e})
        if creds.lifetime <= 0:
            raise ClientError("Authentication expired", errno.EPROTO)
        return creds
