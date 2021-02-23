#!/bin/bash

function apply_license {
 temp_file=$(mktemp)

 cat << HEREDOC > $temp_file
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

HEREDOC

 cat $1 >> $temp_file

 mv $temp_file $1
}


FILES_1=$(find {pyrandall,tests} -type f -name "*.py")
FILES_2=$(find {pyrandall,examples} -type f -name "*.yaml")
for f in $FILES_1 $FILES_2; do
 apply_license $f;
done
