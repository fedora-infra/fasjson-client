import pytest

from fasjson_client.client import Client
from fasjson_client.errors import APIError


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


def test_api_error(server):
    server.mock_endpoint(
        "/me/",
        status_code=500,
        reason="Server Error",
        json={"message": "Something's wrong"},
    )
    with pytest.raises(APIError) as e:
        client = Client("http://example.com/fasjson")
        client.whoami()
    exc = e.value
    assert exc.code == 500
    assert exc.message == "Something's wrong"
    assert exc.data.get("body") == {"message": "Something's wrong"}


def test_api_error_text(server):
    server.mock_endpoint(
        "/me/", status_code=500, reason="Server Error", text="Internal Server Error",
    )
    with pytest.raises(APIError) as e:
        client = Client("http://example.com/fasjson")
        client.whoami()
    exc = e.value
    assert exc.code == 500
    assert exc.message == "500 Server Error: Internal Server Error"
    assert exc.data.get("body") == "Internal Server Error"
