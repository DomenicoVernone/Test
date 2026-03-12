#!/bin/sh

export SUBJECTS_DIR=/root/pipeline/data/output/subjects_directory_output_of_freesurfer

lista=/root/pipeline/data/lista_esempio.txt
filerisultati=/root/pipeline/data/output/subjects_directory_output_of_freesurfer/output_processo.txt


cat ${lista} | while read riga ; do

    dirnifti=`echo ${riga} | awk '{print$1}' | awk 'NR ==1 {print $1}'` ;
    sub=`echo ${riga} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;

    echo comincio ${sub} - `date`  >> ${filerisultati}
    cd /root/pipeline/data/output/subjects_directory_output_of_freesurfer
    recon-all -subject ${sub} -i ${dirnifti} -all
    echo terminato ${sub} - `date`  >> ${filerisultati}


done
