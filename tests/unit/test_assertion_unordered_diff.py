import pytest

from unittest.mock import MagicMock

from pyrandall.reporter import ResultSet
from pyrandall.types import UnorderedCompare


@pytest.fixture
def resultset():
    return MagicMock(spec=ResultSet, unsafe=True)


def test_python_like_json_equals(resultset):
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "b"})

    obj = UnorderedCompare(a)
    assert obj.eval(b)


def test_json_equals(resultset):
    a = """{"foo": "bar", "x": {"a": "b"}}"""
    b = """{"foo": "bar", "x": {"a": "b"}}"""

    obj = UnorderedCompare(a)
    assert obj.eval(b)


def test_two_fields_not_equals(resultset):
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "x"})

    obj = UnorderedCompare(a)
    assert obj.eval(b) is False
