from types import SimpleNamespace
from unittest import mock

import requests_mock


class FasJsonMock:
    def __init__(
        self, spec, url, api_version=1, principal="dummy@EXAMPLE.TEST",
    ):
        self.spec = spec
        self.url = url
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        self.api_version = api_version
        self.principal = principal
        self.gssapi_creds = mock.patch(
            "gssapi.Credentials", return_value=SimpleNamespace(lifetime=10)
        )
        self.reqs = requests_mock.Mocker()

    def start(self):
        self.gssapi_creds.start()
        self.reqs.start()
        self.reqs.get(f"{self.url}/specs/v{self.api_version}.json", text=self.spec)

    def stop(self):
        self.reqs.stop()
        self.gssapi_creds.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def mock_endpoint(self, url, method="GET", **kwargs):
        if self.reqs is None:
            return RuntimeError("You must enter FasJsonMock's context manager first")
        if url.startswith("/"):
            url = url[1:]
        url = f"{self.url}/v{self.api_version}/{url}"
        headers = {"Content-Type": "application/json"}
        headers.update(kwargs.pop("headers", {}))
        self.reqs.register_uri(method, url, headers=headers, **kwargs)
