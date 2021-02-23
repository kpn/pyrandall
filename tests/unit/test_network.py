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

from pyrandall.network import join_urlpath


def test_urljoin_accepts_none():
    url = "http://localhost.com/foo"
    result = join_urlpath(url, None)
    assert "http://localhost.com/foo" == result


def test_urljoin_append_slash():
    url = "http://localhost.com"
    result = join_urlpath(url, "/")
    assert "http://localhost.com/" == result


def test_urljoin_joins_two_paths():
    url = "http://localhost.com/foo"
    result = join_urlpath(url, "/bar")
    assert "http://localhost.com/foo/bar" == result


def test_urljoin_avoids_double_slashes():
    url = "http://localhost.com/foo/"
    result = join_urlpath(url, "/bar")
    assert "http://localhost.com/foo/bar" == result
