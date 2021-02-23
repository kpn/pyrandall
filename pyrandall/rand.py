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

import random
import time


class RandFunctions:

    date_format = "%Y-%m-%d %H:%M"

    def __init__(self, seed=None, k=30):
        random.seed(seed)
        self.size = k

    def rand(self):
        return random.getrandbits(self.size)

    def time(self):
        start = time.mktime(time.strptime("1916-04-30 00:00", self.date_format))
        ptime = start + self.rand() - start
        return time.localtime(ptime)

    def format_date(self, t):
        return time.strftime(self.date_format, t)

    def format_epoch(self, t):
        return time.strftime("%s", t)
