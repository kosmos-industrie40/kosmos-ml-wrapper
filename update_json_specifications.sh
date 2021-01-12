#!/bin/bash

cd src/ml_wrapper/messaging/json_handling

rm -rf kosmos_json_specifications

git clone https://gitlab.inovex.de/proj-kosmos/documentation/specifications/kosmos-json-specifications.git kosmos_json_specifications

cd kosmos_json_specifications

rm -rf .git

find . -mindepth 2 -type d -not \( -name "analysis" -o -name "data" -o -name "ml-trigger" \) -exec rm -rf {} \;

find . -type f -not -name *.json -exec rm -rf {} \;

find . -type d -empty -exec rm -rf {} \;

find . -type d -exec touch {}/__init__.py \;
