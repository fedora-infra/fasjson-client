import pytest

from fasjson_client.client import Client
from fasjson_client.response import PaginationError


def test_response_paged(server):
    mocked = {
        "result": [{"username": "dummy1"}, {"username": "dummy2"}],
        "page": {
            "total_results": 52,
            "page_size": 2,
            "page_number": 1,
            "total_pages": 26,
        },
    }
    server.mock_endpoint("/users/", json=mocked)
    client = Client("http://example.com/fasjson")
    response = client.list_users()
    assert response.result == mocked["result"]
    assert response.page == mocked["page"]
    assert str(response) == str(mocked["result"])
    assert repr(response) == "<FASJSONResponse for list_users()>"
    with pytest.raises(PaginationError):
        response.prev_page()
    response.next_page()
    assert server.reqs.last_request.qs == {"page_size": ["2"], "page_number": ["2"]}


def test_response_single_page(server):
    mocked = {"result": []}
    server.mock_endpoint("/users/", json=mocked)
    client = Client("http://example.com/fasjson")
    response = client.list_users()
    assert response.result == mocked["result"]
    assert response.page is None
    with pytest.raises(PaginationError):
        response.prev_page()
    with pytest.raises(PaginationError):
        response.next_page()


def test_response_wrapper(server):
    """Make sure attributes are forwarded to the operation"""
    client = Client("http://example.com/fasjson")
    operation = client.list_users
    assert operation.consumes == ["application/json"]
    assert operation.produces == ["application/json"]
