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

from unittest import mock
from unittest.mock import MagicMock

import pytest

from pyrandall.executors import BrokerKafka
from pyrandall.reporter import Reporter
from pyrandall.spec import BrokerKafkaSpec
from pyrandall.types import Assertion, ExecutionMode


@pytest.fixture
def reporter():
    return Reporter().scenario("pytest example scenario")


@pytest.fixture
def reporter_1():
    return MagicMock(assertion=MagicMock(spec_set=Assertion), unsafe=True)


def new_executor(assertions):
    spec = BrokerKafkaSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        topic="foo",
        assertions=assertions,
    )
    return BrokerKafka(spec)


MESSAGE_JSON = b'{\n  "uri": "iphone://settings/updates",\n  "session": "111",\n  "timestamp": 2\n}\n'


# @mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume")
# def test_executor_fails_zero_assertions(kafka_mock, reporter_1):
#     spec = MagicMock(
#         unsafe=True, execution_mode=ExecutionMode.VALIDATING, assertions={}
#     )
#     executor = BrokerKafka(spec)
#     result = executor.execute(reporter_1)
#     reporter_1.assertion_failed.assert_called_with(mock.ANY)


# given consumer returns a list with 0 messages
@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume", return_value=[])
def test_validate_fail_zero_messages(kafka_mock, reporter_1):
    # when the expected value is 1
    validator = new_executor({"total_events": 1})
    # and it is executed
    validator.execute(reporter_1)
    # then report that a assertion failed
    reporter_1.assertion_failed.assert_called_with(
        mock.ANY, "total amount of received events"
    )


@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume")
def test_validate_fail_one_messages_body(kafka_mock, reporter_1):
    # given a value that is empty json
    kafka_mock.return_value = [{"value": b"{}"}]
    # and a assertion on a full example json
    validator = new_executor(
        {"total_events": 1, "unordered": [{"value": MESSAGE_JSON}]}
    )
    validator.execute(reporter_1)
    reporter_1.assertion_passed.assert_called_with(mock.ANY)
    # then validate fails
    reporter_1.assertion_failed.assert_called_with(mock.ANY, "unordered events")


@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume")
def test_validate_matches_all(kafka_mock, reporter_1):
    # given a message with bytes json
    kafka_mock.return_value = [MESSAGE_JSON]
    # and validators that asserts 1 message and 1 message value
    validator = new_executor(
        {"total_events": 1, "unordered": [MESSAGE_JSON]}
    )
    validator.execute(reporter_1)
    reporter_1.assertion_failed.assert_not_called()
    # then validate passes on the message count and body compare
    assert (
        2 == reporter_1.assertion_passed.call_count
    ), 'expected method "assertion_passed(ANY)" to be called twice'
