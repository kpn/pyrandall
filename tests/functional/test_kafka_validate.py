import pytest
from freezegun import freeze_time

from pyrandall import cli
from tests.conftest import vcr
from tests.helper import KafkaProducer

TEST_TOPIC = "pyrandall-tests-e2e-processed"


config = "examples/config/v1.json"
MOCK_ARGV = ["--config", config, "--dataflow", "examples/", "validate"]


# freeze time in order to hardcode timestamps
@freeze_time("2012-01-14 14:33:12")
@vcr.use_cassette("test_ingest_to_kafka")
def test_validate_consumes_event():
    producer = KafkaProducer(TEST_TOPIC)
    # producer.send(b'{"id": "bar"}')

    # run validate to consume a message from kafka
    # running following command:
    argv = MOCK_ARGV + ["v2_ingest_kafka_small.yaml"]
    print(f"running {argv}")
    with pytest.raises(SystemExit) as context:
        cli.start(argv)
    if context.value.code == 2:
        pytest.fail(cli.argparse_error(argv))
    assert context.value.code == 0
