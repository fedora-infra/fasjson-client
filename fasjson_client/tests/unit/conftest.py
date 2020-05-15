import os

import pytest

from .utils import FasJsonMock


@pytest.fixture
def fixture_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "fixtures")


@pytest.fixture
def server(fixture_dir):
    with open(f"{fixture_dir}/spec.json") as f:
        spec = f.read()
    with FasJsonMock(spec=spec, url="http://example.com/fasjson") as server:
        yield server
