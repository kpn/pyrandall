import os
import pytest
from freezegun import freeze_time

import threading
from pyrandall import cli
from tests.conftest import vcr
from tests.helper import KafkaProducer
from pyrandall.kafka import KafkaSetupError

TOPIC_1 = "pyrandall-tests-validate-1"
TOPIC_2 = "pyrandall-tests-validate-2"


config = "examples/config/v1.json"
MOCK_ARGV = ["--config", config, "--dataflow", "examples/", "validate"]


def test_error_on_connection_timeout(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:3330")
    argv = MOCK_ARGV + ["v2_ingest_kafka_small.yaml"]
    with pytest.raises(KafkaSetupError) as e:
        cli.start(argv)


# freeze time in order to hardcode timestamps
@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_received_no_events(monkeypatch, kafka_cluster_info):
    # run validate to consume a message from kafka
    # running following command:
    argv = MOCK_ARGV + ["v2_ingest_kafka_small.yaml"]
    print(f"running {argv}")
    with pytest.raises(SystemExit) as context:
        cli.start(argv)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(argv))

    # exit code should be 1 (error)
    assert context.value.code == 1

def produce_events():
    # produce the events
    producer = KafkaProducer(TOPIC_1)
    producer.send(b'{"click": "three"}')
    producer.send(b'{"click": "one"}')
    producer.send(b'{"click": "two"}')

    producer = KafkaProducer(TOPIC_2)
    producer.send(b'{"click": "three"}')

@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_validate_unordered_passed(monkeypatch, kafka_cluster_info):
    # run validate to consume a message from kafka
    # running following command:
    argv = MOCK_ARGV + ["v2_ingest_kafka_small.yaml"]

    print(f"running {argv}")
    with pytest.raises(SystemExit) as context:
        t = threading.Thread(target=produce_events)
        t.start()
        cli.start(argv)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(argv))

    # exit code should be 1 (error)
    assert context.value.code == 0


