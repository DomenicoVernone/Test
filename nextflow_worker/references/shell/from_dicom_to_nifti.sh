#!/usr/bin/env bash
set -euo pipefail

lista="$1"
outdir="$2"

cat "${lista}" | while read riga ; do

    path_soggetto=$(echo "${riga}" | awk '{print $1}')
    nome_soggetto=$(echo "${riga}" | awk '{print $2}')

    mkdir -p "${outdir}/${nome_soggetto}"

    dcm2niix \
        -o "${outdir}/${nome_soggetto}" \
        -f %n_%i_%p_%t \
        -z y \
        "${path_soggetto}"

    rm -f "${outdir}/${nome_soggetto}"/*.json

    echo "${nome_soggetto} $(date)"

done