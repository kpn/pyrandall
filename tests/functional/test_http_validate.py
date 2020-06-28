import pytest
from click.testing import CliRunner

from pyrandall import cli

ARGV_HTTP_VALIDATE_1_OK = [
    "--config",
    "examples/config/v1.json",
    "-V",
    "examples/scenarios/http/validate_ok_status_code.yaml",
]
ARGV_HTTP_VALIDATE_STAUTS_CODE_FAIL = [
    "--config",
    "examples/config/v1.json",
    "-V",
    "examples/scenarios/http/validate_bad_status_code.yaml",
]


def test_validate_assertions_pass(vcr):
    with vcr.use_cassette("test_validate_assertions_pass") as cassette:
        runner = CliRunner()
        result = runner.invoke(cli.main, ARGV_HTTP_VALIDATE_1_OK, catch_exceptions=False)
        assert 'Usage: pyrandall' not in result.output
        assert result.exit_code == 0
        assert cassette.all_played


def test_validate_fail_status_code(vcr):
    with vcr.use_cassette("test_validate_fail_status_code") as cassette:
        runner = CliRunner()
        result = runner.invoke(cli.main, ARGV_HTTP_VALIDATE_STAUTS_CODE_FAIL, catch_exceptions=False)

        assert 'Usage: pyrandall' not in result.output
        assert result.exit_code == 1
        assert cassette.all_played
