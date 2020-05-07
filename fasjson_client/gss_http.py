import errno

import gssapi
from requests_gssapi import HTTPSPNEGOAuth
from bravado import requests_client

from .errors import ClientError


class GssapiHttpClient(requests_client.RequestsClient):
    """HTTP client class used in SwaggerClient for GSSAPI authentication."""

    def __init__(self, *args, principal=None, **kwargs):
        self.principal = principal
        super().__init__(*args, **kwargs)

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

    def authenticated_request(self, request_params):
        """
        Retrieves an authentication token from kerberos
        and adds it in the http header request.
        """
        request_params["auth"] = HTTPSPNEGOAuth(creds=self._get_creds())
        return super().authenticated_request(request_params)
