import json
import types

import bravado
import pytest
import requests
import requests_mock
import gssapi

from fasjson_client.client import Client
from fasjson_client import errors


def test_api_success(fixture_dir, mocker):
    G = mocker.patch("gssapi.Credentials")
    G.return_value = types.SimpleNamespace(lifetime=10)
    mocked = {"response": {"raw": "foo@bar"}}

    with open(f"{fixture_dir}/spec.json") as f:
        data = json.load(f)
    c = Client.from_spec(data, principal="admin@EXAMPLE.TEST")

    with requests_mock.mock() as m:
        m.get("http://fasjson.example.test/fasjson/v1/me", text=json.dumps(mocked))
        output = json.loads(c.me.whoami().response().result)

    assert mocked == output


def test_api_custom_host_success(fixture_dir, mocker):
    G = mocker.patch("gssapi.Credentials")
    G.return_value = types.SimpleNamespace(lifetime=10)
    mocked = {"response": {"raw": "foo@bar"}}

    with open(f"{fixture_dir}/spec.json") as f:
        data = json.load(f)
    c = Client.from_spec(
        data,
        base_url="http://fasjson.fedora.org/fasjson/v1",
        principal="admin@EXAMPLE.TEST",
    )

    with requests_mock.mock() as m:
        m.get("http://fasjson.fedora.org/fasjson/v1/me", text=json.dumps(mocked))
        output = json.loads(c.me.whoami().response().result)

    assert mocked == output


def test_api_custom_host_error(fixture_dir, mocker):
    G = mocker.patch("gssapi.Credentials")
    G.return_value = types.SimpleNamespace(lifetime=10)

    with open(f"{fixture_dir}/spec.json") as f:
        data = json.load(f)

    with pytest.raises(errors.ClientError) as e:
        Client.from_spec(data, base_url="foobar", principal="admin@EXAMPLE.TEST")
    err = e.value

    assert {"base_url": "foobar"} == err.data


def test_api_auth_error(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f:
        data = json.load(f)

    c = Client.from_spec(data, principal="admin@EXAMPLE.TEST")
    with pytest.raises(errors.ClientError) as e:
        c.me.whoami().response().result
    err = e.value
    expected = {
        "trace": '<bound method GSSError.gen_message of GSSError("Major (851968): Unspecified GSS failure.  Minor code may provide more information, Minor (2529639053): Can\'t find client principal admin@EXAMPLE.TEST in cache collection",)>',
        "codes": {
            "maj": 851968,
            "min": 2529639053,
            "routine": 851968,
            "supplementary_code": None,
        },
    }

    assert expected == err.data
