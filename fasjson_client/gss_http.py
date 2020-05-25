import errno

import gssapi
from requests_gssapi import HTTPSPNEGOAuth
from bravado import requests_client

from .errors import ClientSetupError


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
            name = None
        else:
            name = gssapi.Name(self.principal, gssapi.NameType.kerberos_principal)
        try:
            creds = gssapi.Credentials(name=name, usage="initiate")
        except gssapi.exceptions.GSSError as e:
            raise ClientSetupError(
                "Authentication failed", errno.EPROTO, data={"exc": e}
            )
        try:
            # Accessing the lifetime property is sufficient to trigger ExpiredCredentialsError if
            # the lifetime is <= 0
            creds.lifetime
        except gssapi.exceptions.ExpiredCredentialsError:
            raise ClientSetupError("Authentication expired", errno.EPROTO)
        return creds
