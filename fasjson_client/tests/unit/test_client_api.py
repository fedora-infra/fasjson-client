import pytest

from fasjson_client.client import Client


def test_api_success(server):
    mocked = {"result": {"dn": "SRV/foo@bar,dc=example.test", "service": "SRV/foo"}}
    server.mock_endpoint("/me/", json=mocked)
    client = Client("http://example.com/fasjson")
    response = client.whoami()
    assert response.result == mocked["result"]


def test_api_unknown_operation(server):
    client = Client("http://example.com/fasjson")
    with pytest.raises(AttributeError) as e:
        client.unknown_op()
    assert str(e.value) == "No such operation: 'unknown_op'"


def test_api_list_operations(server):
    client = Client("http://example.com/fasjson")
    assert client.operations == [
        "sign_csr",
        "get_cert",
        "list_groups",
        "get_group",
        "get_group_members",
        "whoami",
        "list_users",
        "get_user",
    ]
