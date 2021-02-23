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

import requests

from pyrandall.types import Assertion

from .common import Executor


class RequestHttp(Executor):
    def __init__(self, spec, *args, **kwargs):
        super().__init__()
        self.execution_mode = spec.execution_mode
        self.spec = spec

    def execute(self, reporter):
        spec = self.spec
        if len(spec.assertions) == 0:
            # TODO: Reporter should say "zero assertions found / specified"
            return False

        # TODO: assert / tests the request happened without exceptions
        # act on __exit__ codes
        # with Assertion("response", spec.assertions, "http response", reporter) as a:
        if spec.body:
            response = requests.request(
                spec.method, spec.url, headers=spec.headers, data=spec.body
            )
        else:
            response = requests.request(spec.method, spec.url, headers=spec.headers)

        assertions = []
        with Assertion(
            "status_code", spec.assertions, "http response status_code", reporter
        ) as a:
            assertions.append(a)
            a.actual_value = response.status_code

        with Assertion("body", spec.assertions, "http response body", reporter) as a:
            # a.result = event.json_deep_equals(a.expected, response.content)
            assertions.append(a)
            a.actual_value = response.content

        # TODO: depricate this, not functioally needed anymore
        return all([a.passed() for a in assertions])

    # TODO: move this to reporter
    def create_jsondiff(self, expected, actual):
        print("Output data different")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")

    def represent(self):
        return f"RequestHttp {self.spec.execution_mode.represent()} {self.spec.method} to {self.spec.url}"


class RequestHttpEvents(Executor):
    def __init__(self, spec, *args, **kwargs):
        super().__init__()
        self.execution_mode = spec.execution_mode
        self.spec = spec
        self.nr_of_requests = len(spec.requests)

    def execute(self, reporter):
        if self.nr_of_requests == 0:
            # TODO: Reporter should say "zero events found / specified"
            return False
        return all([RequestHttp(r).execute(reporter) for r in self.spec.requests])

    def represent(self):
        return f"RequestHttpEvents {self.spec.execution_mode.represent()} {self.nr_of_requests} events"
