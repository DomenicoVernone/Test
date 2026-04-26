#!/usr/bin/env bash
set -euo pipefail

lista="$1"
setting="$2"
path="$3"

cat "${lista}" | while read riga ; do

    name=$(echo "${riga}" | awk '{print $2}')

    pyradiomics \
        "${path}/${name}_esempio.csv" \
        -o "${path}/${name}_feat_esempio.csv" \
        --param "${setting}" \
        -f csv \
        --jobs 4

done