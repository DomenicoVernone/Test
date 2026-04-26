#!/usr/bin/env bash
set -euo pipefail

export SUBJECTS_DIR="$1"
lista="$2"
logfile="$3"

cat "${lista}" | while read riga ; do

    dirnifti=$(echo "${riga}" | awk '{print $1}')
    sub=$(echo "${riga}" | awk '{print $2}')

    echo "Start ${sub} $(date)" >> "${logfile}"

    recon-all \
        -subject "${sub}" \
        -i "${dirnifti}" \
        -all \
        -openmp 8

    echo "End ${sub} $(date)" >> "${logfile}"

done