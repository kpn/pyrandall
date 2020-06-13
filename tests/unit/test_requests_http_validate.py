from unittest.mock import MagicMock, call, patch

import pytest

from pyrandall.executors import RequestHttp
from pyrandall.reporter import Reporter
from pyrandall.spec import RequestHttpSpec
from pyrandall.types import Assertion, ExecutionMode
from tests.conftest import vcr


@pytest.fixture
def reporter():
    return Reporter().create_and_track_resultset()


@pytest.fixture
def reporter_1():
    return MagicMock(assertion=MagicMock(spec_set=Assertion), unsafe=True)


@pytest.fixture
def validator_1():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        url="http://localhost:5000/foo/1",
        events=[],
        method="GET",
        headers=[],
        assertions={"status_code": 404},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_3():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers=[],
        url="http://localhost:5000/foo/2",
        assertions={"body": b'{"foo": 2, "bar": false}'},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_4():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers=[],
        url="http://localhost:5000/foo/2",
        assertions={"status_code": 201, "body": b'{"foo": 2, "bar": false}'},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_5():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers=[],
        url="http://localhost:5000/foo/2",
        assertions={"status_code": 201, "body": b'{"foo": 2'},
    )
    return RequestHttp(spec)


def test_validate_makes_get(validator_1, reporter):
    with vcr.use_cassette("test_http_executor_validate_makes_get") as cassette:
        result = validator_1.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/1"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 404
        if cassette.rewound:
            assert cassette.all_played

        assert result


def test_executor_fails_zero_assertions(reporter):
    spec = MagicMock(
        unsafe=True, execution_mode=ExecutionMode.VALIDATING, assertions=[]
    )
    executor = RequestHttp(spec)
    result = executor.execute(reporter)
    assert result is False


def test_validate_makes_get_and_matches_body(validator_3, reporter):
    with vcr.use_cassette(
        "test_http_executor_validate_makes_get_and_matches_body"
    ) as cassette:
        result = validator_3.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played

        assert result


def test_validate__matches_body_not_status(validator_4, reporter):
    with vcr.use_cassette(
        "test_http_executor_validate__matches_body_and_status"
    ) as cassette:
        result = validator_4.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played

        assert result is False


@patch("pyrandall.executors.requests_http.Assertion")
def test_validate_body_and_status_do_not_match(assertion, validator_5, reporter_1):
    with vcr.use_cassette(
        "test_http_executor_validate_body_and_status_do_not_match"
    ) as cassette:
        validator_5.execute(reporter_1)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played

    assert assertion.call_count == 2
    assert (
        call(
            "status_code",
            {"status_code": 201, "body": b'{"foo": 2'},
            "http response status_code",
            reporter_1,
        )
        in assertion.mock_calls
    )
    assert (
        call(
            "body",
            {"status_code": 201, "body": b'{"foo": 2'},
            "http response body",
            reporter_1,
        )
        in assertion.mock_calls
    )
