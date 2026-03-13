workflow {
    // ==========================================
    // 1. INGRESSO DATI (Biforcazione MLOps vs Ricerca)
    // ==========================================
    if (params.containsKey('image') && params.image) {
        // MODO CLINICAL TWIN: Singolo paziente dalla Dashboard
        def nifti_file = file(params.image)
        def subject_id = nifti_file.name.tokenize('.')[0] // Usa il nome del file generato da FastAPI
        def FTD_group = "clinical_patient"
        
        subjects_ch = channel.of(tuple(FTD_group, nifti_file, subject_id))
        
        // Forziamo le cartelle di output dentro la cartella condivisa temporanea del Backend!
        if (params.containsKey('outdir') && params.outdir) {
            params.segmenter_folder_output = "${params.outdir}/segmentation"
            params.features_output = "${params.outdir}/csv_interim"
            params.feat_output = params.outdir 
        }
    } else {
        // MODO RICERCA ORIGINALE: Batch Processing
        subjects_ch = channel
            .fromList(params.dataset)
            .map { folder -> 
                file("${folder}/*.nii*") 
                def FTD_group = file(folder).name
                return tuple(file("${folder}/*.nii*"), FTD_group)
                }
            .transpose()
            .map { nifti, FTD_group->
                def filename = nifti.name
                def subject_id = (filename =~ /^NIFD_([0-9]*_S_[0-9]*)_.*/)
                .findResult { _match, id -> id }
                return tuple(FTD_group, nifti, subject_id)
            }
    }

    // ==========================================
    // 2. CARICAMENTO FILE CONFIGURAZIONE
    // ==========================================
    labels_file_ch = channel.fromPath(params.labels)
    segmenter_dir_ch = channel.fromPath(params.segmenter_folder_output, type: 'dir')
    params_file_ch = channel.fromPath(params.settings)
    features_ch = channel.fromPath(params.features_output, type: 'dir')

    // ==========================================
    // 3. ESECUZIONE PIPELINE
    // ==========================================
    if (params.brain_segmenter == "freesurfer") {
        segmenter_out = freesurfer(subjects_ch)
    } else if (params.brain_segmenter == "fastsurfer"){
        segmenter_out = fastsurfer(subjects_ch, file(params.license))
    } else {
        error("Invalid brain segmenter specified. Use 'freesurfer' or 'fastsurfer'")
    }
    
    nifti_out = nifti_converter(
        segmenter_out,
        params.segmenter_folder_output
        )
    roi = roi_creator(
        nifti_out.combine(labels_file_ch),
        params.segmenter_folder_output
        )
    csv_out = csv_collector(
        segmenter_out.collect(),
        roi.collect(), 
        segmenter_dir_ch, 
        labels_file_ch, 
        )
    feature_extraction(
        csv_out, 
        features_ch, 
        labels_file_ch, 
        params_file_ch,
        )
}


process freesurfer {
    errorStrategy params.error_strategy
    publishDir "${params.segmenter_folder_output}/${FTD_group}", mode: 'copy', pattern: "${subject}"
    maxForks params.maxforks

    input:
    tuple val(FTD_group), file(nifti), val(subject)

    output:
    tuple val(subject), path("${subject}",  type: 'dir'), val(FTD_group)

    script:
    """
    export SUBJECTS_DIR=\$PWD   
    recon-all -subject ${subject} -i ${nifti} -all -cw256
    """
}

process fastsurfer {
    errorStrategy params.error_strategy
    publishDir "${params.segmenter_folder_output}/${FTD_group}", mode: 'copy', pattern: "${subject}"
    maxForks params.maxforks

    input:
    tuple val(FTD_group), file(nifti), val(subject)
    file license
 
    output:
    tuple val(subject), path("${subject}", type: 'dir'), val(FTD_group)
 
    script:
    """
    T1_PATH=\$(realpath ${nifti})
    export FS_LICENSE=\$PWD/${license}

    run_fastsurfer.sh \\
        --t1 \$T1_PATH \\
        --sid ${subject} \\
        --sd \$PWD \\
        --fs_license \$PWD/${license} \\
        ${params.fastsurfer_3T ? '--3T' : ''} --fsaparc \\
        --device ${params.fastsurfer_device} --threads ${params.fastsurfer_threads} --allow_root
    """
}

process nifti_converter {
    publishDir "${params.segmenter_folder_output}/${FTD_group}/${subject}/mri", mode: 'copy'

    input:
    tuple val(subject), path(subject_dir), val(FTD_group)
    val segmenter_folder_output

    output:
    tuple val(subject), val(FTD_group), path("nu.nii"), path("aparc+aseg.nii")

    script:
    """
    export FS_LICENSE=/app/license.txt
    
    mri_convert  ${subject_dir}/mri/nu.mgz nu.nii
    mri_convert ${subject_dir}/mri/aparc+aseg.mgz aparc+aseg.nii
    """
}

process roi_creator {
    publishDir "${params.segmenter_folder_output}/${FTD_group}/${subject}/mri", mode: 'copy', pattern: "ROI"

    input:
    tuple val(subject), val(FTD_group), path(nu_nii), path(aparc_aseg_nii), path(labels_file)
    val(segmenter_folder_output)

    output:
    tuple val(subject), path("ROI")

    script:
    """
    export FS_LICENSE=/app/license.txt
    
    mkdir -p ROI
    cd ROI

    while IFS='\t' read -r roi_id label name || [[ -n "\$label" ]]; do
        if [[ -z "\$label" || "\$label" == "#"* ]]; then
            continue
        fi

        clean_name=\$(echo "\$name" | tr -d '[:space:]' | tr -cd '[:alnum:]_-')
        if [[ -z "\$clean_name" ]]; then
            continue
        fi

        mri_binarize --i ../${aparc_aseg_nii} --match \$label --o \${clean_name}.nii.gz
    done < ../${labels_file}
    """
}

process csv_collector {
    publishDir "${params.features_output}", mode: 'copy'

    input:
    //execution after segmentation
    val(segmenter_out)
    val(roi)

    path subjects_dir
    path labels_file

    output:
    path ("*.csv")

    script:
    """
    REAL_SUBJECTS_DIR=\$(readlink -f ${subjects_dir})

    while IFS='\t' read -r roi_id label name || [[ -n "\$label" ]]; do
        if [[ -z "\$label" || "\$label" == "#"* ]]; then
            continue
        fi

        clean_name=\$(echo "\$name" | tr -d '[:space:]' | tr -cd '[:alnum:]_-')
        if [[ -z "\$clean_name" ]]; then
            continue
        fi

        echo "Image,Mask" > \${clean_name}.csv
        find "\$REAL_SUBJECTS_DIR" -name 'nu.nii' -type f | sort > brain_images.txt
        while IFS= read -r image_path; do
            mask_path="\${image_path%/nu.nii}/ROI/\${clean_name}.nii.gz"
            if [[ -f "\${mask_path}" ]]; then
                echo "\${image_path},\${mask_path}" >> \${clean_name}.csv
            fi
        done < brain_images.txt
        rm -f brain_images.txt
    done < ${labels_file}
    """
}

process feature_extraction {
    publishDir "${params.feat_output}", mode: 'copy'

    input:
    path csv_files
    path features_dir
    path labels_file
    path settings

    output:
    path ("*_feat.csv"), optional: true
    path ("radiomics_features.csv"), optional: true

    script:
    """
    ROI_LIST_PATH="${labels_file}"

    while IFS='\t' read -r roi_id label name || [[ -n "\$label" ]]; do
        if [[ -z "\$label" || "\$label" == "#"* ]]; then
            continue
        fi

        clean_name=\$(echo "\$name" | tr -d '[:space:]' | tr -cd '[:alnum:]_-')
        if [[ -z "\$clean_name" ]]; then
            continue
        fi

        input_csv="\${clean_name}.csv"
        if [[ -f "\${input_csv}" ]]; then
            pyradiomics "\${input_csv}" -o "\${clean_name}_feat.csv" --param "${settings}" -f csv --jobs ${params.pyradiomics_jobs}
        fi
    done < "\${ROI_LIST_PATH}"

    # --- NUOVA AGGREGAZIONE PYTHON (Sostituisce awk) ---
    cat << 'EOF' > aggregate.py
import pandas as pd
import glob

# Cerca tutti i file creati da pyradiomics nella cartella di lavoro corrente
all_files = glob.glob('*_feat.csv')
dfs = []

for f in all_files:
    roi = f.replace('_feat.csv', '')
    try:
        df = pd.read_csv(f)
        cols = [c for c in df.columns if not c.startswith('diagnostics_')]
        df = df[cols].rename(columns=lambda c: f'{roi}_' + c)
        dfs.append(df)
    except Exception:
        pass

if dfs:
    final_df = pd.concat(dfs, axis=1)
    # Lo salva nella cartella corrente, ci penserà Nextflow a spostarlo in outdir!
    final_df.to_csv('radiomics_features.csv', index=False)
    print('✅ File radiomics_features.csv generato!')
else:
    print('❌ Nessun file _feat.csv trovato.')
    # Crea un file vuoto per evitare crash totali
    open('radiomics_features.csv', 'w').close()
EOF

    python3 aggregate.py
    """
}