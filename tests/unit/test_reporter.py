from unittest.mock import MagicMock

import pytest

from pyrandall.reporter import Reporter
from pyrandall.types import AssertionCall


@pytest.fixture
def assertion():
    return MagicMock()


def test_a_group_result_passed(assertion):
    r = Reporter()
    rs = r.create_and_track_resultset()
    rs.assertion_passed(assertion)
    assert r.passed()


def test_a_group_result_failed(assertion):
    r = Reporter()
    rs = r.create_and_track_resultset()
    rs.assertion_passed(assertion)
    rs.assertion_failed(assertion, "body field")
    assert not r.passed()


def test_a_group_result_empty_fails(assertion):
    r = Reporter()
    r.create_and_track_resultset()
    # did not call assertion_failed or assertion_failed
    assert not r.passed()


def test_reporter_result_passed(assertion):
    r = Reporter()
    rs1 = r.create_and_track_resultset()
    rs1.assertion_passed(assertion)
    rs2 = r.create_and_track_resultset()
    rs2.assertion_passed(assertion)
    assert r.passed()


def test_reporter_result_not_passed(assertion):
    r = Reporter()
    rs1 = r.create_and_track_resultset()
    rs1.assertion_failed(assertion, "foo")
    rs2 = r.create_and_track_resultset()
    rs2.assertion_passed(assertion)
    assert not r.passed()


def test_reporter_result_empty_fails(assertion):
    r = Reporter()
    assert not r.passed()


def test_get_failures():
    # given two assertions
    a1 = AssertionCall(1)
    a1.actual_value = 4

    a2 = AssertionCall("foo")
    a2.actual_value = "foo"

    r = Reporter()
    assert 0 == len(r.failures)
    rs1 = r.create_and_track_resultset()
    rs1.assertion_failed(a1, "users created")
    rs1.assertion_passed(a2)

    assert not r.passed()

    failures = r.failed_assertions()
    assert 1 == len(failures)
    f1 = failures[0]
    assert "assertion failed, expected 1, but got 4" == str(f1)
