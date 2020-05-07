import json

from fasjson_client.client import Client


def test_api_success(server):
    mocked = {"result": {"dn": "SRV/foo@bar,dc=example.test", "service": "SRV/foo"}}
    server.mock_endpoint("/me/", json=mocked)
    client = Client("http://example.com/fasjson")
    output = json.loads(client.me.whoami().response().result)
    assert mocked == output
