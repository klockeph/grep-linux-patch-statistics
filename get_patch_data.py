#!/usr/bin/env python3

# Copyright 2018 Philipp Klocke, BMW AG
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

import argparse
import csv
import functools
import re

from datetime import datetime
from subprocess import check_call, check_output, STDOUT


def get_timestamp(version):
    timestamp = check_output(["git", "log", version, "--pretty=format:'%ad'", "--date", "unix", "-1"], stderr=STDOUT).decode('utf-8').replace("'", "")
    return int(timestamp)


def count_commits_by_shas(commits, sha_lookup):
    commits_filtered = 0
    for c in commits:
        if c.split(" ")[0] in sha_lookup:
            commits_filtered += 1
    return commits_filtered


def get_commits_single(version, grep_filter, sha_lookup):
    command = ["git", "log", version, "--format=format:%H", "--no-merges"]
    if grep_filter is not None:
        command = command + ["--grep", grep_filter]

    commits = check_output(command, stderr=STDOUT).decode('utf-8').split('\n')[:-1]
    time = get_timestamp(version)
    if sha_lookup is None:
        return time, len(commits)
    else:
        return time, count_commits_by_shas(commits, sha_lookup)


def get_commits_diff(version, previous, grep_filter, sha_lookup):
    command = ["git", "log", previous+".."+version, "--format=format:%H", "--no-merges"]
    if grep_filter is not None:
        command = command + ["--grep", grep_filter]

    commits = check_output(command, stderr=STDOUT).decode('utf-8').split('\n')[:-1]
    time = get_timestamp(version)
    if sha_lookup is None:
        return time, len(commits)
    else:
        return time, count_commits_by_shas(commits, sha_lookup)


def get_commits_ordered(versions, grep_filter, sha_lookup, start_zero):
    """Note that this method only works if versions are ordered and build on each other"""
    numbers = {}
    start_time, start_commits = get_commits_single(versions[0], grep_filter, sha_lookup)
    if start_zero:
        prev = (versions[0], (start_time, 0))
    else:
        prev = (versions[0], (start_time, start_commits))
    numbers[versions[0]] = prev[1]
    for v in versions[1:]:
        date, n = get_commits_diff(v, prev[0], grep_filter, sha_lookup)
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
        writer.writerow(["version", "timestamp", "patches"])
        for key, value in numbers.items():
            writer.writerow([key, value[0], value[1]])


def get_commits_dot_zero(grep_filter, sha_lookup, start_zero):
    return get_commits_ordered(sorted(
                get_dot_zero_versions(),
                key=functools.cmp_to_key(kernel_version_comparator)),
            grep_filter, sha_lookup, start_zero)


def get_commits_lts(version, grep_filter, sha_lookup, start_zero):
    versions = sorted(
            [v for v in get_versions() if v == version or v.startswith(version+".")],
            key=functools.cmp_to_key(kernel_version_comparator))

    return get_commits_ordered(versions, grep_filter, sha_lookup, start_zero)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter")
    parser.add_argument("-p", "--prefix", default="patch_data")
    parser.add_argument("-v", "--version", help="Aggregate stats for a single (LTS) version")
    parser.add_argument("-s", "--sha_file", help="File containing SHAs (one per line). All other SHAs will be ignored")
    parser.add_argument("-0", "--start_zero", help="Ignore commits before given version, by setting start to zero", action='store_true')
    args = parser.parse_args()

    print("prefix:", args.prefix)
    print("filter:", args.filter)

    sha_lookup = None

    if args.sha_file:
        # generate lookup for SHAs
        sha_lookup = {}
        with open(args.sha_file, "r") as f:
            for sha in f.readlines():
                sha = sha.strip()
                if len(sha) > 0:
                    sha_lookup[sha] = True

    if args.version:
        # generate stats for args.version until linux-<args.version>.y
        if not args.version.startswith('v'):
            print("Version has to be a valid git-tag (e.g. 'v4.1')")
            exit(-1)
        write_to_file(args.prefix + "_" + args.version + "_filtered.csv", get_commits_lts(args.version, args.filter, sha_lookup, args.start_zero))
    else:
        # generate stats for base-versions and LTS-versions
        with open("lts_versions") as f:
            lts_versions = [v.strip() for v in f.read().split(" ")]

        write_to_file(args.prefix + "_zero.csv", get_commits_dot_zero(args.filter, sha_lookup, args.start_zero))
        for v in lts_versions:
            print(v)
            write_to_file(args.prefix + "_" + v + ".csv", get_commits_lts(v, args.filter, sha_lookup, args.start_zero))


if __name__ == "__main__":
    main()
