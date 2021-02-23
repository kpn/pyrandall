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
import re

import jsonschema
import yaml

import pyrandall.behaviors
from pyrandall.exceptions import InvalidSchenarioVersion
from pyrandall.types import (
    Adapter,
    BrokerKafkaSpec,
    ExecutionMode,
    RequestEventsSpec,
    RequestHttpSpec,
)

from .network import join_urlpath

DIR_PATH_DEFAULT = "."

DIR_PYRANDALL_HOME = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_SCENARIO_V2 = os.path.join(DIR_PYRANDALL_HOME, "schemas/scenario/v2.yaml")

VERSION_SCENARIO_V2 = "scenario/v2"
VERSIONS = [VERSION_SCENARIO_V2]


class V2Factory(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def feature(self, data):
        return Feature(self, data["feature"], **self.kwargs)

    def scenario_group(self, nr, data):
        return ScenarioGroup(nr, data, **self.kwargs)


class SpecBuilder:
    def __init__(self, specfile, scenarios_dirname="scenarios", **kwargs):
        self.factory = V2Factory(**kwargs)
        dataflow_path = kwargs.get("dataflow_path", DIR_PATH_DEFAULT)
        self.scenario_file = os.path.join(dataflow_path, scenarios_dirname, specfile)

    def feature(self):
        # creating Feature object will marshall everything below it
        return self.factory.feature(self.load_spec())

    def load_spec(self):
        # TODO: prevent reading sensitive files from filesystem
        with open(self.scenario_file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # implicitly assume scenario v2 schema
            version = data.get("version", VERSION_SCENARIO_V2)
            if version not in VERSIONS:
                raise InvalidSchenarioVersion(VERSIONS)
            # raises errors if unvalid to jsonschema
            jsonschema.validate(data, self.scenario_v2_schema())
            return data

    def scenario_v2_schema(self):
        with open(SCHEMAS_SCENARIO_V2) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)


class ScenarioGroup(object):
    """
    a "feature" holds the list of "scenarios"
    each _scenario_ only has *one simulate* block and *one validate* block
    but both can contain an array of events / request / messages
    these we abstract into tasks called _executors_

    A scenario containing one simulate and one validate task
    tasks = [
        (SimulateTask, BrokerKafkaSpec)
        (Validate, BrokerKafkaSpec)
    ]

    A scenario can contain many requests
    tasks = [
        (SimulateTask, RequestHttpEvents)
        (SimulateTask, RequestHttpEvents)
        (SimulateTask, RequestHttpEvents)
        (Validate, BrokerKafkaSpec)
    ]
    """

    def __init__(
        self,
        nr,
        data,
        dataflow_path=DIR_PATH_DEFAULT,
        events_dirname="events",
        results_dirname="results",
        default_request_url=None,
        schemas_url=None,
        # some tests don't pass this argument, but should
        # TODO: remove default argument?
        hook=pyrandall.behaviors,
        **kwargs,
    ):

        self.events_path = os.path.join(dataflow_path, events_dirname)
        self.results_path = os.path.join(dataflow_path, results_dirname)
        self.nr = nr
        self.description = data["description"]

        self.default_request_url = default_request_url
        if not schemas_url:
            raise ValueError("missing argument schemas_url")
        self.schema_server_url = schemas_url
        self.hook = hook
        self.simulate_tasks = self.build_simulate_tasks(data)
        self.validate_tasks = self.build_validate_tasks(data)

    def build_simulate_tasks(self, data):
        out = []
        item = data["simulate"]
        if item["adapter"] == "requests/http":
            for spec in item["requests"]:
                o = self.build_simulate_request_events_spec(spec)
                out.append(o)

        if item["adapter"] == "broker/kafka":
            self.simulate_adapter = Adapter.BROKER_KAFKA
            for spec in item["messages"]:
                o = self.build_simulate_broker_spec(spec)
                out.append(o)
        return out

    def build_simulate_request_events_spec(self, spec):
        # build according to scenario/v2 schema
        assert "events" in spec
        # TODO: response.status_code is validated implicitly against 204
        # this should be added to the scenario/v2 as assertion to overwrite
        spec["assert_that_responded"] = {"status_code": {"equals_to": 204}}
        out = []
        for fpath in spec.get("events", []):
            o = self.build_simulate_request(spec, fpath)
            out.append(o)
        del spec["assert_that_responded"]
        return RequestEventsSpec(requests=out, adapter=Adapter.REQUEST_HTTP_EVENTS)

    def build_simulate_request(self, spec, fpath):
        if self.default_request_url is None:
            raise ValueError(
                f"self.default_request_url is {self.default_request_url}. "
                "See README.md on how to configure a request URL."
            )
        assertions = {}
        atr = spec.get("assert_that_responded", {})
        assertions.update(self.flatten_assertions(Adapter.REQUESTS_HTTP, atr))
        request = self.parse_http_request_template(fpath)
        # build according to scenario/v2 schema
        return RequestHttpSpec(
            execution_mode=ExecutionMode.SIMULATING,
            assertions=assertions,
            method=request.get("method", spec.get("method", "POST")),
            url=join_urlpath(self.default_request_url, spec.get("path", None)),
            headers=request.get("headers", {}),
            body=request.get("body", None),
            adapter=None
        )

    def build_simulate_broker_spec(self, spec):
        events = []
        for fpath in spec.get("events", []):
            events.append(self.parse_broker_produce_template(fpath))

        assertions = {"events_produced": {"equals_to": len(events)}}
        return BrokerKafkaSpec(
            execution_mode=ExecutionMode.SIMULATING,
            adapter=Adapter.BROKER_KAFKA,
            events=events,
            assertions=self.flatten_assertions(Adapter.BROKER_KAFKA, assertions),
            topic=spec["topic"],
        )

    # functions related to validate specs
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def build_validate_tasks(self, data):
        out = []
        item = data["validate"]
        if item["adapter"] == "requests/http":
            for spec in item["requests"]:
                o = self.build_validate_request_spec(spec)
                out.append(o)

        if item["adapter"] == "broker/kafka":
            for spec in item["messages"]:
                o = self.build_validate_broker_spec(spec)
                out.append(o)
        return out

    def build_validate_request_spec(self, spec):
        if self.default_request_url is None:
            raise ValueError(
                f"self.default_request_url is {self.default_request_url}. "
                "See README.md on how to configure a request URL."
            )
        assertions = {}
        atr = spec.get("assert_that_responded", {})
        assertions.update(self.flatten_assertions(Adapter.REQUESTS_HTTP, atr))

        # build according to scenario/v2 schema
        return RequestHttpSpec(
            execution_mode=ExecutionMode.VALIDATING,
            adapter=Adapter.REQUESTS_HTTP,
            assertions=assertions,
            method=spec.get("method", "GET"),
            url=join_urlpath(self.default_request_url, spec.get("path", None)),
            headers={},
            body=None,
        )

    def build_validate_broker_spec(self, spec):
        assertions = self.broker_assertions(spec)
        return BrokerKafkaSpec(
            execution_mode=ExecutionMode.VALIDATING,
            adapter=Adapter.BROKER_KAFKA,
            events=[],
            assertions=assertions,
            topic=spec["topic"],
        )

    def flatten_assertions(self, adapter, raw):
        out = {}
        for key, value in raw.items():
            if "equals_to" in value:
                out[key] = value["equals_to"]
            if "equals_to_event" in value:
                out[key] = self.format_equals_to_event_file(
                    adapter, value["equals_to_event"]
                )
            if "timeout_after" == key:
                out[key] = self.convert_timeout(value)
        return out

    def broker_assertions(self, spec):
        adapter = Adapter.BROKER_KAFKA
        assertions = {}
        if "assert_that_empty" in spec:
            # alias for more verbose syntax like:
            # is it enough?
            assertions.update(
                self.flatten_assertions({"total_events": {"equals_to": 0}})
            )
        elif (
            "assert_that_received" in spec
            and "unordered" in spec["assert_that_received"]
        ):
            sub = spec["assert_that_received"]
            assertions.update(self.flatten_assertions(adapter, sub))
            assertions.update(
                {
                    "messages": [
                        self.flatten_assertions(adapter, {"value": item})
                        for item in sub["unordered"]
                    ]
                }
            )
        return assertions

    def convert_timeout(self, timeout):
        # timeout can be '10s' , '10m', '10ms'
        ms = re.compile(r"[0-9]*ms$")
        m = re.compile(r"[0-9]*m$")
        s = re.compile(r"[0-9]*s$")
        if ms.match(timeout):
            return int(timeout[0:-2]) / 1000
        elif m.match(timeout):
            return float(timeout[0:-1]) * 60
        elif s.match(timeout):
            return float(timeout[0:-1])
        else:
            return ValueError(
                f"timeout {timeout} format is not supported, valid exampes: 10s, 10m, 10ms"
            )

    def parse_http_request_template(self, fpath):
        with open(self.build_event_path(fpath), "r") as f:
            return self.hook.pyrandall_parse_http_request_template(
                filename=fpath, data=f.read()
            )

    def parse_broker_produce_template(self, fpath):
        with open(self.build_event_path(fpath), "r") as f:
            return self.hook.pyrandall_parse_broker_produce_template(
                filename=fpath, data=f.read()
            )

    def format_equals_to_event_file(self, adapter, fpath):
        with open(self.build_result_path(fpath), "r") as f:
            if adapter == Adapter.REQUESTS_HTTP:
                return self.hook.pyrandall_format_http_request_equals_to_event(
                    filename=fpath, data=f.read()
                )
            if adapter == Adapter.BROKER_KAFKA:
                return self.hook.pyrandall_format_kafka_equals_to_event(
                    filename=fpath, data=f.read()
                )

    def build_event_path(self, fname):
        return os.path.join(self.events_path, fname)

    def build_result_path(self, fname):
        return os.path.join(self.results_path, fname)


class Feature:
    def __init__(self, factory, data, **kwargs):
        self.description = data["description"]
        self.factory = factory
        self.scenario_items = self.build_scenarios(data["scenarios"])

    def build_scenarios(self, scenarios_list):
        return [
            self.factory.scenario_group(i, data)
            for i, data in enumerate(scenarios_list)
        ]
