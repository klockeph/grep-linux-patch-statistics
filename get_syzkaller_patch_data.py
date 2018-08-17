#!/usr/bin/env python3

# Copyright 2018 Philipp Klocke
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

import csv
import functools
import re

from datetime import datetime
from subprocess import check_call, check_output, STDOUT


def get_timestamp(version):
    timestamp = check_output(["git", "log", version, "--pretty=format:'%ad'", "--date", "unix", "-1"], stderr=STDOUT).decode('utf-8').replace("'", "")
    return int(timestamp)


def get_commits_single(version):
    commits = check_output(["git", "log", version, "--grep", "syzkaller.appspotmail.com", "--oneline"], stderr=STDOUT).decode('utf-8').split('\n')[:-1]
    return get_timestamp(version), len(commits)


def get_commits_diff(version, previous):
    commits = check_output(["git", "log", previous+".."+version, "--grep", "syzkaller.appspotmail.com", "--oneline"], stderr=STDOUT).decode('utf-8').split('\n')[:-1]
    return get_timestamp(version), len(commits)


def get_commits_ordered(versions):
    """Note that this method only works if versions are ordered and build on each other"""
    numbers = {}
    prev = versions[0], get_commits_single(versions[0])
    numbers[versions[0]] = prev[1]
    for v in versions[1:]:
        date, n = get_commits_diff(v, prev[0])
        prev = v, (date, n + prev[1][1])
        numbers[v] = prev[1]

    return numbers


def get_versions():
    versions = check_output(["git", "tag"], stderr=STDOUT).decode('utf-8')
    return [v for v in versions.split('\n')[:-1] if not ("-rc" in v or "v2" in v)]


def get_dot_zero_versions():
    versions = get_versions()
    return [v for v in versions if not re.fullmatch(r'.*\..*\..*', v)]


def kernel_version_comparator(v1, v2):
    if v1 == '': v1 = '0'
    if v2 == '': v2 = '0'

    v1 = v1.replace('v', '').split('.', 1)
    v2 = v2.replace('v', '').split('.', 1)
    vv1 = int(v1[0])
    vv2 = int(v2[0])
    if vv1 < vv2:
        return -1
    elif vv1 > vv2:
        return 1
    elif vv1 == vv2:
        if vv1 == 0:
            return 0
        if len(v1) < len(v2):
            return -1
        elif len(v1) > len(v2):
            return 1
    return kernel_version_comparator(v1[1], v2[1])


def write_to_file(filename, numbers):
    with open(filename, 'w+') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["version", "timestamp", "syzkaller_patches"])
        for key, value in numbers.items():
            writer.writerow([key, value[0], value[1]])


def get_commits_dot_zero():
    return get_commits_ordered(sorted(
                get_dot_zero_versions(),
                key=functools.cmp_to_key(kernel_version_comparator)))


def get_commits_lts(version):
    versions = sorted(
            [v for v in get_versions() if v.startswith(version)],
            key=functools.cmp_to_key(kernel_version_comparator))

    return get_commits_ordered(versions)


lts_versions = ["v3.2", "v3.16", "3.18", "v4.4", "v4.9", "v4.14", "v4.17"]

write_to_file("syzkaller_zero.csv", get_commits_dot_zero())
for v in lts_versions:
    print(v)
    write_to_file("syzkaller_" + v + ".csv", get_commits_lts(v))

