// ==========================================
// 0. PARAMETRI DI DEFAULT
// ==========================================
params.outdir = "/shared_data/nf_output"
params.segmenter_folder_output = "${params.outdir}/segmentation"
params.features_output = "${params.outdir}/features"
params.feat_output = "${params.outdir}/feat"
params.error_strategy = 'ignore'
params.maxforks = 1
params.pyradiomics_jobs = 4
params.fastsurfer_device = 'cpu' // default sicuro - viene sovrasctitto dalla CLI
params.fastsurfer_threads = 8
params.fastsurfer_3T = false
params.brain_segmenter = 'freesurfer'  // default sicuro


workflow {
    if (params.containsKey('image') && params.image) {
        def nifti_file = file(params.image)
        def subject_id = nifti_file.name.tokenize('.')[0]
        def FTD_group = "clinical_patient"
        subjects_ch = channel.of(tuple(FTD_group, nifti_file, subject_id))
    } else {
        subjects_ch = channel
            .fromList(params.dataset)
            .map { folder ->
                def FTD_group = file(folder).name
                return tuple(file("${folder}/*.nii{,.gz}"), FTD_group)   // Accettiamo sia .nii che .nii.gz     
            }
            .transpose()
            .map { nifti, FTD_group ->
                def filename = nifti.name
                def subject_id = (filename =~ /^NIFD_([0-9]*_S_[0-9]*)_.*/)
                    .findResult { _match, id -> id }
                return tuple(FTD_group, nifti, subject_id)
            }
    }

    labels_file_ch = channel.fromPath(params.labels)
    params_file_ch = channel.fromPath(params.settings)

    if (params.brain_segmenter == "freesurfer") {
        segmenter_out = freesurfer(subjects_ch)
    } else if (params.brain_segmenter == "fastsurfer") {
        segmenter_out = fastsurfer(subjects_ch, file(params.license))
    } else {
        error("Segmentatore non valido. Usa 'freesurfer' o 'fastsurfer'")
    }

    nifti_out = nifti_converter(segmenter_out, params.segmenter_folder_output)

    roi = roi_creator(nifti_out.combine(labels_file_ch), params.segmenter_folder_output)

    csv_out = csv_collector(
        nifti_out.join(roi).combine(labels_file_ch)
    )

    feature_extraction(
        csv_out,
        nifti_out.map { subject, FTD_group, nu_nii, aparc_aseg_nii -> nu_nii }.collect(),
        roi.map { subject, roi_dir -> roi_dir }.collect(),
        labels_file_ch,
        params_file_ch
    )
}

process freesurfer {
    container 'clinical-freesurfer'
    errorStrategy params.error_strategy
    publishDir "${params.segmenter_folder_output}/${FTD_group}", mode: 'copy', pattern: "${subject}"
    maxForks params.maxforks

    input:
    tuple val(FTD_group), file(nifti), val(subject)

    output:
    tuple val(subject), path("${subject}", type: 'dir'), val(FTD_group)

    script:
    """
    export SUBJECTS_DIR=\$PWD
    recon-all -subject ${subject} -i ${nifti} -all -cw256 -openmp 16
    """
}

process fastsurfer {
    container 'deepmi/fastsurfer:cuda-v2.4.2'
    containerOptions '--gpus all --user $(id -u):$(id -g) --entrypoint ""'
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
    container 'clinical-freesurfer'
    errorStrategy params.error_strategy
    publishDir "${params.segmenter_folder_output}/${FTD_group}/${subject}/mri", mode: 'copy'

    input:
    tuple val(subject), path(subject_dir), val(FTD_group)
    val segmenter_folder_output

    output:
    tuple val(subject), val(FTD_group), path("nu.nii"), path("aparc+aseg.nii")

    script:
    """
    export FS_LICENSE=/app/license.txt
    mri_convert ${subject_dir}/mri/nu.mgz nu.nii
    mri_convert ${subject_dir}/mri/aparc+aseg.mgz aparc+aseg.nii
    """
}

process roi_creator {
    container 'clinical-fsl'
    errorStrategy params.error_strategy
    publishDir "${params.segmenter_folder_output}/${FTD_group}/${subject}/mri", mode: 'copy', pattern: "ROI"

    input:
    tuple val(subject), val(FTD_group), path(nu_nii), path(aparc_aseg_nii), path(labels_file)
    val segmenter_folder_output

    output:
    tuple val(subject), path("ROI")

    script:
    """
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
        fslmaths ../${aparc_aseg_nii} -thr \$label -uthr \$label \${clean_name}.nii.gz
        if [[ -f "\${clean_name}.nii.gz" ]]; then
            fslmaths \${clean_name}.nii.gz -bin \${clean_name}.nii.gz
        fi
    done < ../${labels_file}
    """
}

process csv_collector {
    container 'clinical-pyradiomics'
    errorStrategy params.error_strategy
    publishDir "${params.features_output}", mode: 'copy'

    input:
    tuple val(subject), val(FTD_group), path(nu_nii), path(aparc_aseg_nii), path(roi_dir), path(labels_file)

    output:
    path("*.csv")

    script:
    """
    while IFS='\t' read -r roi_id label name || [[ -n "\$label" ]]; do
        if [[ -z "\$label" || "\$label" == "#"* ]]; then
            continue
        fi
        clean_name=\$(echo "\$name" | tr -d '[:space:]' | tr -cd '[:alnum:]_-')
        if [[ -z "\$clean_name" ]]; then
            continue
        fi
        mask_path="${roi_dir}/\${clean_name}.nii.gz"
        if [[ -f "\${mask_path}" ]]; then
            echo "Image,Mask" > \${clean_name}.csv
            echo "${nu_nii},\${mask_path}" >> \${clean_name}.csv
        fi
    done < ${labels_file}
    """
}

process feature_extraction {
    container 'clinical-pyradiomics'
    errorStrategy params.error_strategy
    publishDir "${params.outdir}", mode: 'copy', pattern: 'radiomics_features.csv'

    input:
    path csv_files
    path nu_files
    path roi_dirs
    path labels_file
    path settings

    output:
    path("*_feat.csv"), optional: true
    path("radiomics_features.csv"), optional: true

    script:
    """
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
    done < "${labels_file}"

    cat << 'EOF' > aggregate.py
import csv
import glob

all_files = glob.glob('*_feat.csv')
if not all_files:
    print('Nessun file _feat.csv trovato.')
    open('radiomics_features.csv', 'w').close()
else:
    rows = {}
    all_keys = ['Image']
    for f in sorted(all_files):
        roi = f.replace('_feat.csv', '')
        with open(f) as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                img = row.get('Image', '')
                if img not in rows:
                    rows[img] = {'Image': img}
                for k, v in row.items():
                    if k not in ('Image', 'Mask') and not k.startswith('diagnostics_'):
                        new_key = f'{roi}_{k}'
                        rows[img][new_key] = v
                        if new_key not in all_keys:
                            all_keys.append(new_key)
    with open('radiomics_features.csv', 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=all_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows.values())
    print('radiomics_features.csv generato.')
EOF
    python3 aggregate.py
    """
}
