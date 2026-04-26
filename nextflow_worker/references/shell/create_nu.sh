#!/usr/bin/env bash
set -euo pipefail

export SUBJECTS_DIR="$1"
lista="$2"

cat "${lista}" | while read riga ; do

    sogg=$(echo "${riga}" | awk '{print $2}')

    cd "${SUBJECTS_DIR}/${sogg}/mri"

    mri_convert nu.mgz nu.nii

done