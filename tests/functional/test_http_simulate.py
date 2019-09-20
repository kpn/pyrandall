import unittest
from unittest.mock import patch

from pyrandall import cli
from tests.conftest import vcr

ARGV_RESPONSE_200 = [
    "--config",
    "examples/config/v1.json",
    "--dataflow",
    "examples/",
    "simulate",
    "http/simulate_200.yaml",
]
ARGV_RESPONSE_400 = [
    "--config",
    "examples/config/v1.json",
    "--dataflow",
    "examples/",
    "simulate",
    "http/simulate_400.yaml",
]


class SimulatorTest(unittest.TestCase):
    @patch("argparse.ArgumentParser._print_message")
    def test_execute_a_simulation_fails(self, print_message):
        with self.assertRaises(SystemExit) as context:
            cli.start([])
            self.assertEqual(context.exception.code, 2)
            print_message.assert_called_once()

    def test_simulate_json_response_200(self):
        with vcr.use_cassette("test_simulate_json_response_200") as cassette:
            with self.assertRaises(SystemExit) as context:
                cli.start(ARGV_RESPONSE_200)

            assert len(cassette) == 1
            r1 = cassette.requests[0]
            assert r1.path == "/v1/actions/produce-event"
            assert cassette.responses_of(r1)[0]["status"]["code"] == 204
            assert cassette.all_played
            if context.exception.code == 2:
                self.fail(cli.argparse_error(ARGV_RESPONSE_200))

            # not all request had the expected status code (see assertions)
            assert context.exception.code == 0

    def test_simulate_json_response_400(self):
        with vcr.use_cassette("test_simulate_json_response_400") as cassette:
            with self.assertRaises(SystemExit) as context:
                cli.start(ARGV_RESPONSE_400)

            assert len(cassette) == 1
            r0 = cassette.requests[0]
            assert r0.path == "/cant_find_this"
            assert cassette.responses_of(r0)[0]["status"]["code"] == 404
            assert cassette.all_played
            if context.exception.code == 2:
                self.fail(cli.argparse_error(ARGV_RESPONSE_400))

            assert context.exception.code == 1


if __name__ == "__main__":
    unittest.main()
