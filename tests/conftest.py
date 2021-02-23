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

import vcr
import pytest

from confluent_kafka.admin import AdminClient, ClusterMetadata

defaults = ["method", "scheme", "host", "port", "path", "query"]
vcr = vcr.VCR(
    cassette_library_dir="tests/fixtures/vcr",
    # record_mode =  [once, new_episodes, none, all]
    # https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    record_mode=os.environ.get("VCR_MODE", "once"),
    match_on=(defaults + ["body", "headers"]),
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
)


@pytest.fixture
def kafka_cluster_info() -> ClusterMetadata:
    # this fixture can be used to assert the connection is configured
    # correctly and functioning
    kafka = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    admin = AdminClient({"bootstrap.servers": kafka})
    cluster = admin.list_topics()
    assert ('{1: BrokerMetadata(1, %s)}' % kafka) == str(cluster.brokers)
    return cluster
