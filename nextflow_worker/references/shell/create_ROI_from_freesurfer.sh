#!/bin/sh

lista_roi=/root/pipeline/data/all_freesurfer_labels.txt
lista_sogg=/root/pipeline/data/lista_esempio.txt

cat ${lista_sogg} | while read riga_1 ; do

	sogg=`echo ${riga_1} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;

	cd /root/pipeline/data/output/subjects_directory_output_of_freesurfer/${sogg}/mri
	mri_convert nu.mgz nu.nii
	mri_convert aparc+aseg.mgz aparc+aseg.nii
	mkdir ROI
	cd ./ROI

	cat ${lista_roi} | while read riga ; do

    		label=`echo ${riga} | awk '{print$1}' | awk 'NR ==1 {print $1}'` ;
    		name=`echo ${riga} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;

    		fslmaths /root/pipeline/data/output/subjects_directory_output_of_freesurfer/${sogg}/mri/aparc+aseg.nii -thr ${label} -uthr ${label} ${name}.nii.gz
    		fslmaths ${name}.nii.gz -bin ${name}.nii.gz

	done

done






