import pytest

from pyrandall import const
from pyrandall.executors import RequestHttp
from pyrandall.spec import RequestHttpSpec
from pyrandall.types import ExecutionMode
from pytest_httpserver import HeaderValueMatcher

STATUS_CODE_ASSERTION = {"status_code": 201}


@pytest.fixture
def request_http_spec():
    return RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b'{"foo": "bar"}',
        method="POST",
        headers={},
    )

@pytest.fixture
def executor_http(request_http_spec):
    return RequestHttp(request_http_spec)

@pytest.fixture
def vcr_headers_filter():
    return []

@pytest.fixture
def vcr_match_on():
    return []

def test_header_present(httpserver, executor_http, reporter, vcr):
    with vcr.use_cassette("test_http_user_agent") as cassette:
        result = executor_http.execute(reporter)

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.method == 'POST'
        assert len(r0.headers) == 5
        assert 'User-Agent' in r0.headers
        agent = r0.headers['User-Agent']
        assert agent.startswith("pyrandall/")
        assert agent.split('/')[1] == const.get_version()
