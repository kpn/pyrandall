# Copyright 2019 KPN N.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

from unittest.mock import MagicMock

import pytest

from pyrandall.executors import RequestHttp, RequestHttpEvents
from pyrandall.spec import RequestEventsSpec, RequestHttpSpec
from pyrandall.types import Assertion, ExecutionMode
from tests.conftest import vcr


@pytest.fixture
def reporter():
    return MagicMock(unsafe=True)


@pytest.fixture
def reporter_1():
    return MagicMock(assertion=MagicMock(spec_set=Assertion), unsafe=True)


STATUS_CODE_ASSERTION = {"status_code": 201}


@pytest.fixture
def simulator_1():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b'{"foo": "bar"}',
        method="POST",
        headers=[],
    )
    return RequestHttp(spec)


@pytest.fixture
def simulator_2():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b"",
        method="POST",
        headers=[],
    )
    return RequestHttp(spec)


@pytest.fixture
def simulator_3():
    r1 = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b"",
        method="POST",
        headers=[],
    )
    r2 = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b'{"foo": "bar"}',
        method="POST",
        headers=[],
    )
    spec = RequestEventsSpec(requests=[r1, r2])
    return RequestHttpEvents(spec)


def test_simulate__post_201_repsonse(simulator_1, reporter):
    with vcr.use_cassette("test_http_executor_simulate_post_201") as cassette:
        result = simulator_1.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body == b'{"foo": "bar"}'
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 201
        if cassette.rewound:
            assert cassette.all_played

        assert result


def test_simulate_post_400_response(simulator_2, reporter):
    with vcr.use_cassette("test_http_executor_simulate_post_400_response") as cassette:
        result = simulator_2.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 400
        if cassette.rewound:
            assert cassette.all_played

        assert not result


def test_simulate_fails_zero_requests(reporter):
    spec = RequestEventsSpec(requests=[])
    executor = RequestHttpEvents(spec)
    result = executor.execute(reporter)
    assert not result


def test_simulate_post_200_and_400(simulator_3, reporter):
    with vcr.use_cassette("test_http_executor_simulate_post_201_and_400") as cassette:
        result = simulator_3.execute(reporter)

        assert len(cassette) == 2
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 400

        r1 = cassette.requests[1]
        assert r1.url == "http://localhost:5000/users"
        assert r1.body == b'{"foo": "bar"}'
        response = cassette.responses_of(r1)[0]
        assert response["status"]["code"] == 201
        if cassette.rewound:
            assert cassette.all_played

        assert not result
