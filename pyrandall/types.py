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

from enum import Enum, Flag, auto
from typing import Any, Dict, List, NamedTuple

import jsondiff
from deepdiff import DeepDiff


class ExecutionMode(Enum):
    SIMULATING = auto()
    VALIDATING = auto()

    def represent(self):
        return self.name.lower()


class Adapter(Enum):
    REQUEST_HTTP_EVENTS = "request/http/events"
    REQUESTS_HTTP = "request/http"
    BROKER_KAFKA = "broker/kafka"

    def __str__(self):
        return f"adapter: {self.value}"


class Flags(Flag):
    DESCRIBE = auto()

    BLOCKING = auto()
    # REALTIME = auto()

    SIMULATE = auto()
    VALIDATE = auto()

    BLOCKING_E2E = BLOCKING | SIMULATE | VALIDATE
    # REALTIME_E2E = REALTIME | SIMULATE | VALIDATE

    # def run_realtime(self):
    #     return self & Flags.REALTIME

    def run_blocking(self):
        return self & Flags.BLOCKING

    def has_validate(self):
        return self & Flags.VALIDATE

    def has_simulate(self):
        return self & Flags.SIMULATE


class Assertion:
    def __init__(self, field: str, spec: Dict, on_fail_text, resultset):
        self.field = field
        self.spec = spec
        self.resultset = resultset
        self.on_fail_text = on_fail_text
        if self.field in self.spec:
            self.call = self.create_assertion(self.spec[self.field])
        else:
            self.call = SkipAssertionCall()

    def __enter__(self):
        return self.call

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # TODO: check that no errors where raised
        # (to check a http / socket connection was successfull without exceptions)
        # resultset.raise_error()
        if self.call.called and self.call.result:
            self.resultset.assertion_passed(self.call)
        elif self.call.called:
            self.resultset.assertion_failed(self.call, self.on_fail_text)
        else:
            self.resultset.assertion_skipped(self.call)

    def create_assertion(self, value):
        return AssertionCall(expected_value=value)


class UnorderedDiffAssertion(Assertion):
    def __init__(self, field: str, spec: Dict, on_fail_text, resultset):
        super().__init__(field, spec, on_fail_text, resultset)

    def create_assertion(self, value):
        return UnorderedCompare(expected_value=value)


class AssertionCall:
    def __init__(self, expected_value):
        self.expected = expected_value
        self.actual = None
        self.called = False
        self.result = None

    @property
    def actual_value(self):
        return self.actual

    @actual_value.setter
    def actual_value(self, value):
        self.actual = value
        self.eval(value)

    def eval(self, actual_value):
        self.called = True
        self.result = self.expected == actual_value
        return self.result

    def passed(self):
        return self.called and self.result

    def __str__(self):
        if self.passed():
            return f"assertion passed, expected {self.expected}, and got {self.actual}"
        else:
            return f"assertion failed, expected {self.expected}, but got {self.actual}"


class UnorderedCompare(AssertionCall):
    def __init__(self, expected_value):
        super().__init__(expected_value)
        self.diff = None

    def eval(self, actual_value):
        self.called = True
        self.diff = DeepDiff(
            self.expected,
            actual_value,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
        )
        self.result = self.diff == {}
        return self.result

    def __str__(self):
        if self.passed():
            return super().__str__()
        else:
            return (
                f"assertion failed (unordered json comparison"
                f"got: {self.expected}"
                f"diff: {self.diff}"
                f"See https://github.com/seperman/deepdiff for more info on how to read the diff"
            )


def json_deep_equals(expected, actual):
    result = jsondiff.diff(expected, actual)
    return result == {}


class SkipAssertionCall(AssertionCall):
    def __init__(self):
        super().__init__(None)

    def eval(self, actual_value):
        pass

    def passed(self):
        return True

    def __str__(self):
        return f"assertion skipped"


# implicit Data interface of records below:
# - field execution_mode is present
# - field adapter is constant
# - field assertions is present


class RequestHttpSpec(NamedTuple):
    execution_mode: ExecutionMode
    # general request options
    method: str
    url: str
    headers: Dict[str, str]
    # simulate fields
    body: bytes = None
    # TODO: remove all events from here
    events: List[str] = []
    # validate fields
    # assert_that_responded translated to fields
    assertions: Dict[str, Any] = {}
    adapter: Adapter = Adapter.REQUESTS_HTTP


class RequestEventsSpec(NamedTuple):
    # general request options
    requests: List[RequestHttpSpec]
    execution_mode = ExecutionMode.SIMULATING
    adapter: Adapter = Adapter.REQUESTS_HTTP


class BrokerKafkaSpec(NamedTuple):
    execution_mode: ExecutionMode
    # general broker options
    topic: str
    # simulate fields
    events: List[str] = []
    # validate fields
    # assert_that_responded translated to fields
    assertions: Dict[str, Any] = {}
    adapter: Adapter = Adapter.BROKER_KAFKA


__all__ = [
    "ExecutionMode",
    "Adapter",
    "Flags",
    "Assertion",
    "AssertionCall",
    "SkipAssertionCall",
    "RequestHttpSpec",
    "RequestEventsSpec",
    "BrokerKafkaSpec",
]
