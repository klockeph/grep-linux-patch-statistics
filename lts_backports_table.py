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

import csv
import os

def list_files(version):
    return [f for f in os.listdir() if f.endswith("_" + version + ".csv")]


def main():
    with open("lts_versions") as f:
        lts_versions = [v.strip() for v in f.read().split(" ")]

    versions = {}
    for v in lts_versions:
        versions[v] = {}
        files = list_files(v)
        for f in files:
            tool = f.split("_", 1)[0]
            with open(f) as csvfile:
                reader = list(csv.DictReader(csvfile))
                start = reader[0]['patches']
                end = reader[-1]['patches']
                backports = int(end) - int(start)
            versions[v][tool] = backports
    # versions = {<version>: {<tool>: backports, ..}, ..}

    all_tools = set.union(*[set(versions[v]) for v in versions])

    fieldnames = ["version"]
    fieldnames.extend(sorted(list(all_tools), key=lambda s: s.casefold()))

    with open("LTS_aggregated.csv", "w+") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for v in versions:
            versions[v]
            row = versions[v]
            row.update({"version" : v})
            writer.writerow(row)


if __name__ == "__main__":
    main()
