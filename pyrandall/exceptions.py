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

INVALID_VERSION_MSG = (
    "Unsupported schema version for pyrandall. " "Please choose from: {}"
)


class InvalidSchenarioVersion(Exception):
    def __init__(self, correct_versions):
        super(Exception, self).__init__(
            INVALID_VERSION_MSG.format(", ".join(correct_versions))
        )
