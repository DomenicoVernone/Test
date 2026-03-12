#!/bin/bash
#benedetta

lista=/path_to/lista_dicom.txt
outdir=/path_to_folder_nifti_originali


# cicla sui soggetti
cat ${lista} | while read riga ; do
 path_soggetto=`echo ${riga} | awk '{print$1}' | awk 'NR ==1 {print $1}'` ;
 nome_soggetto=`echo ${riga} | awk '{print$2}' | awk 'NR ==1 {print $1}'` ;
 
 mkdir ${outdir}/${nome_soggetto}
 cd ${path_soggetto}/
 dcm2niix -o ${outdir}/${nome_soggetto} -f %n_%i_%p_%t -z y ${path_soggetto}/
 rm ${outdir}/${nome_soggetto}/*.json
 echo ${nome_soggetto} - `date`


done

