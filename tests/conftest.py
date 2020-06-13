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
