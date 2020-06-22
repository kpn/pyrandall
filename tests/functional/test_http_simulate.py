from tests.conftest import vcr

ARGV_RESPONSE_200 = [
    "--config",
    "examples/config/v1.json",
    "-s",
    "examples/scenarios/http/simulate_200.yaml",
]
ARGV_RESPONSE_400 = [
    "--config",
    "examples/config/v1.json",
    "-s",
    "examples/scenarios/http/simulate_400.yaml",
]


def test_execute_a_simulation_fails(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--config",
        "examples/config/v1.json"
    ])
    assert 'Usage: main' in result.output
    assert result.exit_code == 2

def test_simulate_json_response_200(pyrandall_cli):
    with vcr.use_cassette("test_simulate_json_response_200") as cassette:
        result = pyrandall_cli.invoke(ARGV_RESPONSE_200)
        assert 'Usage: main' not in result.output
        assert result.exit_code == 0

        assert len(cassette) == 1
        r1 = cassette.requests[0]
        assert r1.path == "/v1/actions/produce-event"
        assert cassette.responses_of(r1)[0]["status"]["code"] == 204
        assert cassette.all_played
        # not all request had the expected status code (see assertions)

def test_simulate_json_response_400(pyrandall_cli):
    with vcr.use_cassette("test_simulate_json_response_400") as cassette:
        result = pyrandall_cli.invoke(ARGV_RESPONSE_400)
        assert 'Usage: main' not in result.output
        assert result.exit_code == 1

        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.path == "/cant_find_this"
        assert cassette.responses_of(r0)[0]["status"]["code"] == 404
        assert cassette.all_played
