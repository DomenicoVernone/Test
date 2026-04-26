// ==========================================
// PARAMETRI DI DEFAULT
// ==========================================

params.labels = "${projectDir}/data/external/ROI_labels.tsv"
params.settings = "${projectDir}/data/external/pyradiomics.yaml"

params.outdir = "/shared_data/nf_output"
params.segmenter_folder_output = "${params.outdir}/segmentation"
params.features_output = "${params.outdir}/features"

params.error_strategy = 'terminate'
params.maxforks = 1
params.pyradiomics_jobs = 4

params.fastsurfer_device = 'cpu'
params.fastsurfer_threads = 4
params.fastsurfer_3T = false

params.brain_segmenter = 'freesurfer'


// ==========================================
// WORKFLOW
// ==========================================

workflow {

    labels_file_ch = Channel.fromPath(params.labels)
    params_file_ch = Channel.fromPath(params.settings)


    if (params.image) {

        def nifti_file = file(params.image)
        def subject_id = nifti_file.name.tokenize('.')[0]

        subjects_ch = Channel.of(
            tuple("clinical_patient", nifti_file, subject_id)
        )

    } else {

        error "Parametro --image obbligatorio"
    }


    // =========================
    // SEGMENTAZIONE
    // =========================

    segmenter_out = freesurfer(subjects_ch)


    // =========================
    // MGZ → NIFTI
    // =========================

    nifti_out = nifti_converter(segmenter_out)


    // =========================
    // ROI CREATION
    // =========================

    roi_input = nifti_out.combine(labels_file_ch)

    roi_out = roi_creator(roi_input)


    // =========================
    // CSV GENERATION
    // =========================

    csv_input = nifti_out
        .join(roi_out)
        .combine(labels_file_ch)

    csv_out = csv_collector(csv_input)


    // =========================
    // FEATURE EXTRACTION
    // =========================

    feature_extraction(
        csv_out.collect(),
        labels_file_ch,
        params_file_ch
    )
}


// ==========================================
// FREESURFER
// ==========================================

process freesurfer {

    container 'clinical-freesurfer'

    errorStrategy params.error_strategy

    publishDir "${params.segmenter_folder_output}", mode: 'copy'

    maxForks params.maxforks

    input:
    tuple val(group), file(nifti), val(subject)

    output:
    tuple val(subject), val(group), path("${subject}")

    script:
    """
    export SUBJECTS_DIR=\$PWD

    recon-all \
        -subject ${subject} \
        -i ${nifti} \
        -all \
        -cw256 \
        -openmp 16
    """
}


// ==========================================
// NIFTI CONVERTER
// ==========================================

process nifti_converter {

    container 'clinical-freesurfer'

    errorStrategy 'terminate'

    input:
    tuple val(subject), val(group), path(subject_dir)

    output:
    tuple val(subject),
          val(group),
          path("nu.nii"),
          path("aparc+aseg.nii")

    script:
    """
    mri_convert ${subject_dir}/mri/nu.mgz nu.nii

    mri_convert \
        ${subject_dir}/mri/aparc+aseg.mgz \
        aparc+aseg.nii
    """
}


// ==========================================
// ROI CREATOR
// ==========================================

process roi_creator {

    container 'clinical-fsl'

    errorStrategy params.error_strategy

    publishDir "${params.segmenter_folder_output}", mode: 'copy'

    input:
    tuple val(subject),
          val(group),
          path(nu_nii),
          path(aparc_aseg_nii),
          path(labels_file)

    output:
    tuple val(subject),
          path("ROI")

    script:
    """
    mkdir ROI

    while IFS='\\t' read -r roi_id label name || [[ -n "\$label" ]]
    do

        [[ -z "\$label" ]] && continue
        [[ "\$label" == "#"* ]] && continue

        clean_name=\$(echo "\$name" \
            | tr -d '[:space:]' \
            | tr -cd '[:alnum:]_-')

        [[ -z "\$clean_name" ]] && continue

        fslmaths \
            ${aparc_aseg_nii} \
            -thr \$label \
            -uthr \$label \
            ROI/\${clean_name}.nii.gz

        fslmaths \
            ROI/\${clean_name}.nii.gz \
            -bin \
            ROI/\${clean_name}.nii.gz

    done < ${labels_file}
    """
}


// ==========================================
// CSV COLLECTOR
// ==========================================

process csv_collector {

    container 'clinical-pyradiomics'

    errorStrategy params.error_strategy

    publishDir "${params.features_output}", mode: 'copy'

    input:
    tuple val(subject),
          val(group),
          path(nu_nii),
          path(aparc_aseg_nii),
          path(roi_dir),
          path(labels_file)

    output:
    path("*.csv")

    script:
    """
    while IFS='\\t' read -r roi_id label name || [[ -n "\$label" ]]
    do

        [[ -z "\$label" ]] && continue
        [[ "\$label" == "#"* ]] && continue

        clean_name=\$(echo "\$name" \
            | tr -d '[:space:]' \
            | tr -cd '[:alnum:]_-')

        mask=${roi_dir}/\${clean_name}.nii.gz

        if [[ -f "\$mask" ]]
        then
            echo "Image,Mask" > \${clean_name}.csv
            echo "${nu_nii},\$mask" >> \${clean_name}.csv
        fi

    done < ${labels_file}
    """
}


// ==========================================
// FEATURE EXTRACTION
// ==========================================

process feature_extraction {

    container 'clinical-pyradiomics'

    errorStrategy params.error_strategy

    publishDir "${params.outdir}", mode: 'copy'

    input:
    path csv_files
    path labels_file
    path settings

    output:
    path("radiomics_features.csv")

    script:
    """
    pyradiomics \
        *.csv \
        -o radiomics_features.csv \
        --param ${settings} \
        -f csv \
        --jobs ${params.pyradiomics_jobs}
    """
}