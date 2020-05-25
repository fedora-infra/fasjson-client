import pytest

from fasjson_client.errors import ClientSetupError, APIError


def test_client_error():
    e = ClientSetupError("message", 42, {"foo": "bar"})
    assert str(e) == "message"
    assert repr(e) == "<ClientSetupError code=42 message=message data={'foo': 'bar'}>"


def test_api_error_bad_source():
    with pytest.raises(ValueError):
        APIError.from_bravado_error(RuntimeError("dummy"))
