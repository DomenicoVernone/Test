#!/bin/sh

export SUBJECTS_DIR=/root/pipeline/data/output/subjects_directory_output_of_freesurfer
lista=/root/pipeline/data/lista_esempio.txt

cat ${lista} | while read riga_1 ; do

	sogg=`echo ${riga_1} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;
        echo ${sogg}
	cd /root/pipeline/data/output/subjects_directory_output_of_freesurfer/${sogg}/mri
	mri_convert nu.mgz nu.nii

done

# export SUBJECTS_DIR=/media/benedetta/Volume1/Dati/freesurfer/HC_nostri
# lista=/media/benedetta/Volume/SLA_radiomics/liste/lista_HC_old.txt

# cat ${lista} | while read riga_1 ; do

# 	sogg=`echo ${riga_1} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;
#         echo ${sogg}
# 	cd /media/benedetta/Volume1/Dati/freesurfer/HC_nostri/${sogg}/mri
# 	mri_convert nu.mgz nu.nii

# done

