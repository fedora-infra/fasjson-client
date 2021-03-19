import errno
from urllib.parse import urljoin, urlsplit

from requests.exceptions import RequestException
from bravado import requests_client
from bravado.client import SwaggerClient, CallableOperation
from bravado.exception import HTTPError
from swagger_spec_validator.common import SwaggerValidationError

from .gss_http import GssapiAuthenticator
from .errors import ClientSetupError
from .response import ResponseWrapper


class Client:
    """FASJSON client class that builds API methods based on openapi specs.

    Args:
        url (str): the URL to the FASJSON instance
        principal (str): the Kerberos principal to use for authentication
        api_version (int): the FASJSON API version to use
        bravado_config (dict): additional configuration to pass down to bravado
        auth (bool): whether or not the client should use auth. only for testing.
    """

    def __init__(
        self, url, principal=None, api_version=1, bravado_config=None, auth=True
    ):
        self._base_url = url
        if not self._base_url.endswith("/"):
            self._base_url += "/"
        self._principal = principal
        self._api_version = api_version
        self._bravado_config = bravado_config or {}
        self._auth = auth
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
        if self._auth:
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
            raise ClientSetupError(
                "error loading remote spec, are you sure this is the URL to a FASJSON instance?",
                errno.ECONNABORTED,
                data=data,
            )
        except SwaggerValidationError as e:
            raise ClientSetupError(
                "schema validation failed", errno.EPROTO, data={"exc": e}
            )
        except ValueError as e:
            raise ClientSetupError(
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

    def list_all_entities(self, entity_name, page_size=1000):
        try:
            operation = self._ops["list_{}".format(entity_name)]
        except KeyError:
            raise ValueError(
                "No such entity: {}. Is it plural? It should be.".format(entity_name)
            )
        page_number = 0
        next_page_exists = True
        while next_page_exists:
            page_number += 1
            response = operation(page_size=page_size, page_number=page_number)
            yield from response.result
            next_page_exists = page_number < response.page["total_pages"]
