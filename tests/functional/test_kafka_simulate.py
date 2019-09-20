import pytest
from freezegun import freeze_time

from pyrandall import cli
from tests.conftest import vcr
from tests.helper import KafkaConsumer

TEST_TOPIC = "pyrandall-tests-e2e"


config = "examples/config/v1.json"
MOCK_ARGV = ["--config", config, "--dataflow", "examples/", "simulate"]


def test_invalid_kafka_scenario():
    argv = MOCK_ARGV + ["v2_ingest_kafka_invalid.yaml"]
    with pytest.raises(SystemExit) as context:
        cli.start(argv)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(argv))
    assert context.value.code == 4


# freeze time in order to hardcode timestamps
@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_simulate_produces_event():
    consumer = KafkaConsumer(TEST_TOPIC)
    try:
        highwater = consumer.get_high_watermark()

        # run simulate to create a message to kafka
        # running following command:
        argv = MOCK_ARGV + ["v2_ingest_kafka_small.yaml"]
        print(f"running {argv}")
        with pytest.raises(SystemExit) as context:
            cli.start(argv)
        if context.value.code == 2:
            pytest.fail(cli.argparse_error(argv))
        assert context.value.code == 0

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
