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

import json

import pyrandall


@pyrandall.hookimpl
def pyrandall_cli_banner(config):
    """
    Hook to overwrite banners printed at the
    start of pyrandall cli to stdout
    """
    return config


@pyrandall.hookimpl
def pyrandall_parse_http_request_template(filename, data):
    if filename.find(".json") > 0:
        body = json.dumps(json.loads(data))
        headers = {"content-type": "application/json"}
    else:
        body = data.encode()
        headers = {}

    return {"headers": headers, "body": body}


@pyrandall.hookimpl
def pyrandall_parse_broker_produce_template(filename, data):
    if ".json" in filename:
        output = json.dumps(json.loads(data))
    else:
        output = data

    return output.encode()


@pyrandall.hookimpl
def pyrandall_format_http_request_equals_to_event(filename, data):
    return json.dumps(json.loads(data)).encode()


@pyrandall.hookimpl
def pyrandall_format_kafka_equals_to_event(filename, data):
    # any fileformat will be compared in binary
    return data.encode()
