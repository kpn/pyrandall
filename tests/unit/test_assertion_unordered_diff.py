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

import pytest

from unittest.mock import MagicMock

from pyrandall.reporter import ResultSet
from pyrandall.types import UnorderedCompare


@pytest.fixture
def resultset():
    return MagicMock(spec=ResultSet, unsafe=True)


def test_python_like_json_equals(resultset):
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "b"})

    obj = UnorderedCompare(a)
    assert obj.eval(b)


def test_json_equals(resultset):
    a = """{"foo": "bar", "x": {"a": "b"}}"""
    b = """{"foo": "bar", "x": {"a": "b"}}"""

    obj = UnorderedCompare(a)
    assert obj.eval(b)


def test_two_fields_not_equals(resultset):
    a = dict(foo="bar", x={"a": "b"})
    b = dict(foo="bar", x={"a": "x"})

    obj = UnorderedCompare(a)
    assert obj.eval(b) is False
