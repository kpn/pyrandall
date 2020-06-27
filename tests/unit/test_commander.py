from unittest.mock import MagicMock

import pytest

from pyrandall.commander import Commander, Flags
from pyrandall.reporter import Reporter, ResultSet
from pyrandall.spec import SpecBuilder


@pytest.fixture
def spec():
    builder = SpecBuilder(
        specfile=open("examples/scenarios/one_event.yaml"),
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
        schemas_url="http://localhost:8899/schemas/",
    )
    return builder.feature()


def test_commander_run_one_for_one(spec, vcr):
    with vcr.use_cassette("test_commander_run_one_for_one") as cassette:
        reporter = MagicMock(Reporter(), unsafe=True)
        reporter.create_and_track_resultset.return_value = MagicMock(ResultSet, unsafe=True)

        c = Commander(spec, Flags.E2E)
        c.run(reporter)

        reporter.feature.assert_called_once_with("One event"),
        reporter.scenario.assert_any_call("Send words1 event")
        # at least once called
        reporter.simulate.assert_called()
        reporter.validate.assert_called()
        reporter.run_task.assert_called()
        reporter.print_failures.assert_called_once_with()
        reporter.passed.assert_called_once()
        assert len(cassette) == 2
