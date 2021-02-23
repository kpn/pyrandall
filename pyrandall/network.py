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

import posixpath
from urllib.parse import urljoin, urlparse


def extend_url(base, path):
    url_parsed = urlparse(base)
    # append should not overwrite a path on the base (example: google.com/nl)
    if path[0] == "/":
        sanitized_path = path[1:]
    else:
        sanitized_path = path
    return urljoin(url_parsed.geturl(), posixpath.join(url_parsed.path, sanitized_path))


def join_urlpath(url, urlpath=None):
    if urlpath is None:
        return url
    elif urlpath == "/":
        return url + "/"
    else:
        return extend_url(url, urlpath)
