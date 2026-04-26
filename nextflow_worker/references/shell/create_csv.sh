#!/usr/bin/env bash
set -euo pipefail

lista_roi="$1"
subjects_dir="$2"
target_file="$3"
output_dir="$4"

mkdir -p "${output_dir}"

echo 'Image' > "${output_dir}/brain_esempio.txt"

find "${subjects_dir}" -iname 'nu.nii' | sort -n \
    >> "${output_dir}/brain_esempio.txt"

cat "${lista_roi}" | while read riga ; do

    name=$(echo "${riga}" | awk '{print $2}')

    echo 'Mask' > "${output_dir}/${name}_roi.txt"

    find "${subjects_dir}" -iname "${name}.nii.gz" | sort -n \
        >> "${output_dir}/${name}_roi.txt"

    paste -d "," \
        "${output_dir}/brain_esempio.txt" \
        "${output_dir}/${name}_roi.txt" \
        "${target_file}" \
        > "${output_dir}/${name}_esempio.csv"

done

rm "${output_dir}"/*_roi.txt