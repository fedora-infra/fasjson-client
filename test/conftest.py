import os

import pytest

@pytest.fixture
def test_dir():
  return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def fixture_dir(test_dir):
  return f'{test_dir}/fixtures'
