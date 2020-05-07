from fasjson_client.errors import ClientError


def test_client_error():
    e = ClientError("message", 42, {"foo": "bar"})
    assert str(e) == "message"
    assert repr(e) == "<ClientError code=42 message=message data={'foo': 'bar'}>"
