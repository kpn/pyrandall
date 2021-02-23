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

from pyrandall.commander import Commander, Flags
from pyrandall.reporter import Reporter, ResultSet
from pyrandall.spec import SpecBuilder
from tests.conftest import vcr


@pytest.fixture
def spec():
    builder = SpecBuilder(
        specfile="one_event.yaml",
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
        schemas_url="http://localhost:8899/schemas/",
    )
    return builder.feature()


@vcr.use_cassette("test_commander_run_one_for_one")
def test_commander_run_one_for_one(spec):
    reporter = MagicMock(Reporter(), unsafe=True)
    reporter.create_and_track_resultset.return_value = MagicMock(ResultSet, unsafe=True)

    c = Commander(spec, Flags.BLOCKING_E2E)
    c.run(reporter)

    reporter.feature.assert_called_once_with("One event"),
    reporter.scenario.assert_any_call("Send words1 event")
    # at least once called
    reporter.simulate.assert_called()
    reporter.validate.assert_called()
    reporter.run_task.assert_called()
    reporter.print_failures.assert_called_once_with()
    reporter.passed.assert_called_once()
