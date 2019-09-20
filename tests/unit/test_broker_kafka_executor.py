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
