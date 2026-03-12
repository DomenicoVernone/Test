#!/bin/sh
lista_roi=/root/pipeline/data/all_freesurfer_labels.txt

mkdir -p /root/pipeline/data/output/features
echo 'Image' > /root/pipeline/data/output/features/brain_esempio.txt

find /root/pipeline/data/output/subjects_directory_output_of_freesurfer/ -iname 'nu.nii' | sort -n >> /root/pipeline/data/output/features/brain_esempio.txt

cat ${lista_roi} | while read riga ; do

    	name=`echo ${riga} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;

        echo 'Mask' > /root/pipeline/data/output/features/${name}_roi.txt

        find /root/pipeline/data/output/subjects_directory_output_of_freesurfer/ -iname ${name}.nii.gz | sort -n >> /root/pipeline/data/output/features/${name}_roi.txt

    	paste -d "," /root/pipeline/data/output/features/brain_esempio.txt /root/pipeline/data/output/features/${name}_roi.txt /root/pipeline/data/output/subjects_directory_output_of_freesurfer/target_esempio.txt > /root/pipeline/data/output/features/${name}_esempio.csv

done

rm /root/pipeline/data/output/features/*_roi.txt


