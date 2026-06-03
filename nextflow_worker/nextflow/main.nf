// main.nf — entry point canonico della pipeline Clinical Twin (DSL2)
//
// Uso rapido (single image, modalità clinica — stessa chiamata di nextflow_worker/main.py):
//   nextflow run main.nf -c nextflow.config \
//       --image /shared_data/nifti/scan.nii.gz \
//       --outdir /shared_data/nf_output \
//       --brain_segmenter freesurfer
//
// Uso batch con training (ricerca):
//   nextflow run main.nf -c nextflow.config -c configs/training.config \
//       --dataset '["/data/HC_T1","/data/bvFTD_T1"]' \
//       --run_training true
//
// In produzione, nextflow_worker/main.py chiama preprocessing.nf direttamente.
// Questo file è il punto di ingresso per esecuzioni manuali e CI.

nextflow.enable.dsl = 2

// ──────────────────────────────────────────────────────────────────────────────
// IMPORT processi da preprocessing.nf
// ──────────────────────────────────────────────────────────────────────────────
include { freesurfer }        from './preprocessing.nf'
include { fastsurfer }        from './preprocessing.nf'
include { nifti_converter }   from './preprocessing.nf'
include { roi_creator }       from './preprocessing.nf'
include { csv_collector }     from './preprocessing.nf'
include { feature_extraction } from './preprocessing.nf'

params.run_training = false

// ──────────────────────────────────────────────────────────────────────────────
// WORKFLOW PREPROCESSING (singolo soggetto o batch)
// ──────────────────────────────────────────────────────────────────────────────
workflow PREPROCESS {
    if (params.containsKey('image') && params.image) {
        def nifti_file = file(params.image)
        def subject_id = nifti_file.name.tokenize('.')[0]
        subjects_ch = channel.of(tuple("clinical_patient", file(params.image), subject_id))
    } else {
        subjects_ch = channel
            .fromList(params.dataset)
            .map { folder ->
                def FTD_group = file(folder).name
                return tuple(file("${folder}/*.nii{,.gz}"), FTD_group)
            }
            .transpose()
            .map { nifti, FTD_group ->
                def filename = nifti.name
                def subject_id = (filename =~ /^NIFD_([0-9]*_S_[0-9]*)_.*/)
                    .findResult { _match, id -> id } ?: filename.tokenize('.')[0]
                return tuple(FTD_group, nifti, subject_id)
            }
    }

    labels_file_ch = Channel.value(file(params.labels))
    params_file_ch = channel.fromPath(params.settings)

    if (params.brain_segmenter == "freesurfer") {
        segmenter_out = freesurfer(subjects_ch)
    } else if (params.brain_segmenter == "fastsurfer") {
        segmenter_out = fastsurfer(subjects_ch, file(params.license))
    } else {
        error("Segmentatore non valido. Usa 'freesurfer' o 'fastsurfer'")
    }

    nifti_out = nifti_converter(segmenter_out, params.segmenter_folder_output)
    roi       = roi_creator(nifti_out.combine(labels_file_ch))

    csv_out = csv_collector(
        nifti_out.join(roi)
            .map { subject, group, nu, aparc, group2, roi_dir ->
                tuple(subject, group, nu, aparc, roi_dir)
            }
            .combine(labels_file_ch)
    )

    feature_extraction(
        csv_out,
        nifti_out.map { subject, FTD_group, nu_nii, aparc_aseg_nii -> nu_nii }.collect(),
        roi.map { subject, group, roi_dir -> roi_dir }.collect(),
        labels_file_ch,
        params_file_ch
    )
}

// ──────────────────────────────────────────────────────────────────────────────
// ENTRY POINT
// ──────────────────────────────────────────────────────────────────────────────
workflow {
    PREPROCESS()
}
