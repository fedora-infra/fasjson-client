import errno
from urllib.parse import urljoin

from requests.exceptions import RequestException
from bravado.client import SwaggerClient
from bravado.exception import HTTPError
from swagger_spec_validator.common import SwaggerValidationError

from .gss_http import GssapiHttpClient
from .errors import ClientError


class Client:
    """FASJSON client class that builds API methods based on openapi specs."""

    def __init__(self, url, principal=None, api_version=1, bravado_config=None):
        self._base_url = url
        if not self._base_url.endswith("/"):
            self._base_url += "/"
        self._principal = principal
        self._api_version = api_version
        self._bravado_config = bravado_config or {}
        # self._bravado_config.setdefault("disable_fallback_results", True)
        self._api = self._make_bravado_client()

    @property
    def _spec_url(self):
        return urljoin(self._base_url, f"specs/v{self._api_version}.json")

    def _make_bravado_client(self):
        http_client = GssapiHttpClient(principal=self._principal)
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

    def __getattr__(self, name):
        return getattr(self._api, name)
