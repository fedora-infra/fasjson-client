import os

import pytest
from bravado.client import SwaggerClient

from .utils import FasJsonMock


@pytest.fixture
def fixture_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "fixtures")


@pytest.fixture
def bravado_client(mocker):
    client = mocker.Mock(name="mock SwaggerClient")
    mocker.patch.object(SwaggerClient, "from_url", return_value=client)
    yield client


@pytest.fixture
def server(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f:
        spec = f.read()
    with FasJsonMock(spec=spec, url="http://example.com/fasjson") as server:
        yield server
