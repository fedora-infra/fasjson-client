import errno
from urllib.parse import urljoin, urlsplit

from requests.exceptions import RequestException
from bravado import requests_client
from bravado.client import SwaggerClient, CallableOperation
from bravado.exception import HTTPError
from swagger_spec_validator.common import SwaggerValidationError

from .gss_http import GssapiAuthenticator
from .errors import ClientError
from .response import ResponseWrapper


class Client:
    """FASJSON client class that builds API methods based on openapi specs.

    Args:
        url (str): the URL to the FASJSON instance
        principal (str): the Kerberos principal to use for authentication
        api_version (int): the FASJSON API version to use
        bravado_config (dict): additional configuration to pass down to bravado
    """

    def __init__(self, url, principal=None, api_version=1, bravado_config=None):
        self._base_url = url
        if not self._base_url.endswith("/"):
            self._base_url += "/"
        self._principal = principal
        self._api_version = api_version
        self._bravado_config = bravado_config or {}
        # self._bravado_config.setdefault("disable_fallback_results", True)
        self._api = self._make_bravado_client()
        self._ops = self._make_ops_map()

    @property
    def operations(self):
        """List available operations.

        Returns:
            list(str): available operation names
        """
        return list(self._ops)

    @property
    def _spec_url(self):
        return urljoin(self._base_url, f"specs/v{self._api_version}.json")

    def _make_bravado_client(self):
        http_client = requests_client.RequestsClient()
        server_hostname = urlsplit(self._base_url).netloc
        http_client.authenticator = GssapiAuthenticator(
            server_hostname, principal=self._principal
        )
        try:
            api = SwaggerClient.from_url(
                self._spec_url, http_client=http_client, config=self._bravado_config,
            )
        except (HTTPError, RequestException) as e:
            data = {
                "exc": e,
                "message": str(e),
            }
            if getattr(e, "status_code", None):
                data["status_code"] = e.status_code
            raise ClientError(
                "error loading remote spec", errno.ECONNABORTED, data=data
            )
        except SwaggerValidationError as e:
            raise ClientError("schema validation failed", errno.EPROTO, data={"exc": e})
        except ValueError as e:
            raise ClientError(
                "remote data validation failed", errno.EPROTO, data={"exc": e}
            )
        return api

    def _make_ops_map(self):
        ops = {}
        for res_name, res in self._api.swagger_spec.resources.items():
            for op_name, op in res.operations.items():
                ops[op_name] = ResponseWrapper(CallableOperation(op))
        return ops

    def __getattr__(self, name):
        try:
            return self._ops[name]
        except KeyError:
            raise AttributeError("No such operation: {!r}".format(name))
