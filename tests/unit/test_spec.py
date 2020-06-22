import pytest

from pyrandall.spec import SpecBuilder
from pyrandall.types import BrokerKafkaSpec, RequestEventsSpec, RequestHttpSpec


@pytest.fixture
def feature():
    builder = SpecBuilder(
        specfile=open("examples/scenarios/v2.yaml"),
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
        schemas_url="http://localhost:8899/schemas/",
    )
    return builder.feature()


def test_request_url_missing():
    with pytest.raises(ValueError) as e:
        SpecBuilder(open("examples/scenarios/v2.yaml"), dataflow_path="examples/").feature()
        expected = (
            "self.default_request_url is None. "
            "See README.md on how to configure a request URL."
        )
        assert expected == e.message


def test_description_present(feature):
    assert feature.description == "V2 schema exampe"


def test_scenarios_attributes_present(feature):
    scenarios = feature.scenario_items
    assert len(scenarios) == 2
    scenario_1 = scenarios[0]
    assert scenario_1.description == "HTTP to an ingest API and key-value API"
    scenario_2 = scenarios[1]
    assert scenario_2.description == "Produce and Consumer to kafka"


def test_creates_executors_for_simulate_only(feature):
    simulators = []
    for s in feature.scenario_items:
        for s in s.simulate_tasks:
            simulators.append(s)

    assert len(simulators) == 2
    i1 = simulators.pop()
    assert isinstance(i1, BrokerKafkaSpec)
    i0 = simulators.pop()
    assert isinstance(i0, RequestEventsSpec)


def test_creates_executors_for_validators_only(feature):
    validators = []
    for s in feature.scenario_items:
        for s in s.validate_tasks:
            validators.append(s)

    assert len(validators) == 3
    i3 = validators.pop()
    assert isinstance(i3, BrokerKafkaSpec)
    i2 = validators.pop()
    assert isinstance(i2, BrokerKafkaSpec)
    i1 = validators.pop()
    assert isinstance(i1, RequestHttpSpec)


def test_parse_events_plugins():
    SpecBuilder(
        specfile=open("examples/scenarios/v2.yaml"),
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
        schemas_url="http://localhost:8899/schemas/",
    )
