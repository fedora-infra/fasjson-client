from types import SimpleNamespace

import gssapi
import pytest

from fasjson_client.gss_http import GssapiAuthenticator
from fasjson_client.errors import ClientSetupError


def test_no_principal(mocker):
    gssapi = mocker.patch("fasjson_client.gss_http.gssapi")
    c = GssapiAuthenticator("fasjson.example.com")
    c._get_creds()
    gssapi.Credentials.assert_called_once_with(name=None, usage="initiate")


def test_explicit_principal(mocker):
    gssapi_mock = mocker.patch.multiple(
        "fasjson_client.gss_http.gssapi",
        Name=mocker.DEFAULT,
        Credentials=mocker.DEFAULT,
        NameType=mocker.DEFAULT,
    )
    gssapi_mock["Name"].return_value = name = object()
    gssapi_mock["Credentials"].return_value = credentials = SimpleNamespace(lifetime=10)
    gssapi_mock["NameType"].kerberos_principal = kerberos_principal = object()

    c = GssapiAuthenticator("fasjson.example.com", principal="dummy")
    creds = c._get_creds()

    gssapi_mock["Name"].assert_called_once_with("dummy", kerberos_principal)
    gssapi_mock["Credentials"].assert_called_once_with(name=name, usage="initiate")
    assert creds is credentials


def test_auth_failed(mocker):
    gssapi_mock = mocker.patch("fasjson_client.gss_http.gssapi")
    gssapi_mock.exceptions.GSSError = gssapi.exceptions.GSSError
    gssapi_mock.Credentials.side_effect = gssapi.exceptions.GSSError(851968, 2529639053)
    c = GssapiAuthenticator("fasjson.example.com", principal="dummy")
    with pytest.raises(ClientSetupError) as e:
        c._get_creds()
    err = e.value
    assert "Authentication failed" == str(err)
    assert err.code == 71
    assert "exc" in err.data


def test_auth_expired(mocker):
    class MockCredentials(mocker.Mock):
        @property
        def lifetime(self):
            return self.get_lifetime()

        def get_lifetime(self):
            raise gssapi.exceptions.ExpiredCredentialsError(851968, 2529638944)

    mocker.patch("fasjson_client.gss_http.gssapi.Credentials", new=MockCredentials)
    c = GssapiAuthenticator("fasjson.example.com", principal="dummy")
    with pytest.raises(ClientSetupError) as e:
        c._get_creds()

    err = e.value
    assert "Authentication expired" == str(err)
    assert err.code == 71
