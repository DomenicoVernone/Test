#!/bin/sh

lista=/root/pipeline/data/all_freesurfer_labels.txt
setting=/root/pipeline/params_new.yaml
path=/root/pipeline/data/output/features/

cat ${lista} | while read riga ; do

    name=`echo ${riga} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;

    pyradiomics ${path}/${name}_esempio.csv -o ${path}/${name}_feat_esempio.csv --param ${setting} -f csv --jobs 4

done


