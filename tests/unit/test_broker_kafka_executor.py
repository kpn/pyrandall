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

from pyrandall import executors
from pyrandall.types import BrokerKafkaSpec, ExecutionMode


@pytest.fixture
def spec_1():
    return BrokerKafkaSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions={},
        events=["filename.json"],
        topic="foo",
    )


@pytest.fixture
def reporter():
    return MagicMock(unsafe=True)


def test_represent(spec_1, reporter):
    executor = executors.BrokerKafka(spec_1)
    assert executor.represent() == "BrokerKafka simulating to foo"
