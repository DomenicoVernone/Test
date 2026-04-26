#!/usr/bin/env bash
set -euo pipefail

lista_roi="$1"
lista_sogg="$2"
subjects_dir="$3"

cat "${lista_sogg}" | while read riga_1 ; do

    sogg=$(echo "${riga_1}" | awk '{print $2}')

    cd "${subjects_dir}/${sogg}/mri"

    mri_convert nu.mgz nu.nii
    mri_convert aparc+aseg.mgz aparc+aseg.nii

    mkdir -p ROI
    cd ROI

    cat "${lista_roi}" | while read riga ; do

        label=$(echo "${riga}" | awk '{print $1}')
        name=$(echo "${riga}" | awk '{print $2}')

        fslmaths \
            "${subjects_dir}/${sogg}/mri/aparc+aseg.nii" \
            -thr "${label}" \
            -uthr "${label}" \
            "${name}.nii.gz"

        fslmaths "${name}.nii.gz" -bin "${name}.nii.gz"

    done

done