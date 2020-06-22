import os
import pytest
from freezegun import freeze_time

import threading
from tests.conftest import vcr
from tests.helper import KafkaProducer
from pyrandall.kafka import KafkaSetupError

TOPIC_1 = "pyrandall-tests-validate-1"
TOPIC_2 = "pyrandall-tests-validate-2"

MOCK_ARGV = [
    "--config",
    "examples/config/v1.json",
    "-V"
]
ARGV_SMALL = MOCK_ARGV + ["examples/scenarios/v2_ingest_kafka_small.yaml"]


def produce_events():
    # produce the events
    producer = KafkaProducer(TOPIC_1)
    producer.send(b'{"click": "three"}')
    producer.send(b'{"click": "one"}')
    producer.send(b'{"click": "two"}')

    producer = KafkaProducer(TOPIC_2)
    producer.send(b'{"click": "three"}')


def test_error_on_connection_timeout(monkeypatch, pyrandall_cli):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:3330")
    with pytest.raises(KafkaSetupError) as e:
        pyrandall_cli.invoke(ARGV_SMALL)


# freeze time in order to hardcode timestamps
@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_received_no_events(monkeypatch, kafka_cluster_info, pyrandall_cli):
    """
    run validate to consume a message from kafka
    """
    result = pyrandall_cli.invoke(ARGV_SMALL)
    # exit code should be 1 (error)
    assert 'Usage: main' not in result.output
    print(result.output)
    assert result.exit_code == 1


@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_validate_unordered_passed(kafka_cluster_info, pyrandall_cli):
    produce_events()
    result = pyrandall_cli.invoke(ARGV_SMALL)
    assert 'Usage: main' not in result.output
    assert result.exit_code == 0


