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

import os
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
def test_simulate_produces_event(kafka_cluster_info):
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
