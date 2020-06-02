from unittest.mock import patch

import pytest

from pyrandall import cli
from tests.conftest import vcr

CONFIG = "examples/config/v1.json"
ARGV_HTTP_VALIDATE_1_OK = [
    "--config",
    CONFIG,
    "--dataflow",
    "examples/",
    "sanitytest",
    "http/validate_ok_status_code.yaml",
]
ARGV_HTTP_VALIDATE_STAUTS_CODE_FAIL = [
    "--config",
    CONFIG,
    "--dataflow",
    "examples/",
    "sanitytest",
    "http/validate_bad_status_code.yaml",
]


@patch("pyrandall.cli.ArgumentParser._print_message")
def test_execute_a_sanitytest_fails(print_message):
    with pytest.raises(SystemExit) as context:
        cli.start([])
    assert context.value.code == 2
    print_message.assert_called()


@vcr.use_cassette("test_validate_assertions_pass")
def test_validate_assertions_pass():
    with pytest.raises(SystemExit) as context:
        cli.start(ARGV_HTTP_VALIDATE_1_OK)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(ARGV_HTTP_VALIDATE_1_OK))

    assert context.value.code == 0


@vcr.use_cassette("test_validate_fail_status_code")
def test_validate_fail_status_code():
    with pytest.raises(SystemExit) as context:
        cli.start(ARGV_HTTP_VALIDATE_STAUTS_CODE_FAIL)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(ARGV_HTTP_VALIDATE_STAUTS_CODE_FAIL))

    assert context.value.code == 1
