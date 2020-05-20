import pytest

from fasjson_client.errors import ClientError, APIError


def test_client_error():
    e = ClientError("message", 42, {"foo": "bar"})
    assert str(e) == "message"
    assert repr(e) == "<ClientError code=42 message=message data={'foo': 'bar'}>"


def test_api_error_bad_source():
    with pytest.raises(ValueError):
        APIError.from_bravado_error(RuntimeError("dummy"))
