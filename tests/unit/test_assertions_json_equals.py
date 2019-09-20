from pyrandall.types import json_deep_equals


def test_python_like_json_equals():
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "b"})
    assert json_deep_equals(a, b)


def test_json_equals():
    a = """{"foo": "bar", "x": {"a": "b"}}"""
    b = """{"foo": "bar", "x": {"a": "b"}}"""
    assert json_deep_equals(a, b)


def test_two_fields_not_equals():
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "x"})
    assert json_deep_equals(a, b) is False
