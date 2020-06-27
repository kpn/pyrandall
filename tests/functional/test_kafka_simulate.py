import os
import pytest
from freezegun import freeze_time

from tests.helper import KafkaConsumer


TEST_TOPIC = "pyrandall-tests-e2e"

MOCK_ARGV = [
    "--config",
    "examples/config/v1.json",
    "-s"
]
ARGV_INVALID = MOCK_ARGV + ["examples/scenarios/v2_ingest_kafka_invalid.yaml"]
ARGV_SMALL = MOCK_ARGV + ["examples/scenarios/v2_ingest_kafka_small.yaml"]


def test_fail_on_invaild_schema(pyrandall_cli):
    result = pyrandall_cli.invoke(ARGV_INVALID)
    assert 'Failed validating' in result.output
    assert result.exit_code == 4


@freeze_time("2012-01-14 14:33:12")
def test_simulate_produces_event(kafka_cluster_info, pyrandall_cli):
    consumer = KafkaConsumer(TEST_TOPIC)
    try:
        highwater = consumer.get_high_watermark()

        # run simulate to create a message to kafka
        # running following command:
        result = pyrandall_cli.invoke(ARGV_SMALL)
        assert 'Usage: main' not in result.output
        assert result.exit_code == 0

        messages = consumer.get_messages(expecting=2)
        assert len(messages) == 2
        print(f"highwater: {highwater}, message offset: {messages[1].offset()}")
        assert (
            b'{"uri": "iphone://settings/updates", "session": "111", "timestamp": 2}'
        ) == messages[0].value()

        assert (
            b'{"uri": "iphone://settings/disconnect", "session": "000", "timestamp": 1}'
        ) == messages[1].value()

        # at last, prevent that we always consume the same message
        expected_offset = highwater + 1
        assert expected_offset == messages[1].offset()
    finally:
        consumer.close()
