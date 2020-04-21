import json

import bravado
import pytest
import requests
import requests_mock
from swagger_spec_validator.common import SwaggerValidationError

from fasjson_client.client import Client
from fasjson_client import errors


def test_client_from_spec(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f:
        data = json.load(f)
    c = Client.from_spec(data)

    assert isinstance(c.me.whoami, bravado.client.CallableOperation)


def test_client_from_spec_error(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f:
        data = f.read()
    with pytest.raises(errors.ClientError) as e:
        Client.from_spec(data)
    err = e.value

    assert "schema validation failed" == str(err)
    assert isinstance(err.data["exc"], SwaggerValidationError)
    assert repr(err).startswith("<ClientError code=71 message=schema validation failed")


def test_client_from_url(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f, requests_mock.mock() as m:
        m.get("http://myspec.com", text=f.read())
        c = Client.from_url("http://myspec.com")

    assert isinstance(c.me.whoami, bravado.client.CallableOperation)


def test_client_from_url_parse_error(fixture_dir):
    with open(f"{fixture_dir}/spec.json"), requests_mock.mock() as m, pytest.raises(
        errors.ClientError
    ) as e:
        m.get("http://myspec.com", text="{somethin: {wrong:")
        Client.from_url("http://myspec.com")
    err = e.value

    assert "remote data validation failed" == str(err)
    assert (
        "<ClientError code=71 message=remote data validation failed data=None>"
        == repr(err)
    )


def test_client_from_url_conn_error(fixture_dir):
    with open(f"{fixture_dir}/spec.json"), requests_mock.mock() as m, pytest.raises(
        errors.ClientError
    ) as e:
        m.get("http://myspec.com", exc=requests.exceptions.ConnectTimeout)
        Client.from_url("http://myspec.com")
    err = e.value

    assert "error loading remote spec data" == str(err)
    assert {"trace": "ConnectTimeout()"} == err.data


def test_client_from_url_conn_error_with_request(fixture_dir):
    with open(f"{fixture_dir}/spec.json"), requests_mock.mock() as m, pytest.raises(
        errors.ClientError
    ) as e:

        def text_cb(request, context):
            raise requests.exceptions.ConnectTimeout(request=request)

        m.get("http://myspec.com", text=text_cb)
        Client.from_url("http://myspec.com")
    err = e.value

    assert "error loading remote spec data" == str(err)
    assert {
        "trace": "ConnectTimeout()",
        "request": {"method": "GET", "url": "http://myspec.com/"},
    } == err.data


def test_client_from_url_response_error(fixture_dir):
    with open(f"{fixture_dir}/spec.json"), requests_mock.mock() as m, pytest.raises(
        errors.ClientError
    ) as e:
        m.get("http://myspec.com", text="FORBIDDEN", status_code=403)
        Client.from_url("http://myspec.com")
    err = e.value

    assert "error loading remote spec data" == str(err)
    assert {
        "url": "http://myspec.com/",
        "method": "GET",
        "status_code": 403,
    } == err.data
