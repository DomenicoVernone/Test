// ── Default parameters (override via CLI o configs/training.config) ───────────
params.brain_segmenter    = "fastsurfer"
params.experiment_name    = "hc_vs_bvFTD"
params.selection_method   = "lasso"          // "lasso" o "rfe"
params.sperimental        = "bvFTD"
params.control            = "HC"
params.parallel_training  = true

params.merge_script    = "${projectDir}/../ftd_diagnosis/util/merge_radiomics.r"
params.rfe_script      = "${projectDir}/../ftd_diagnosis/sequential/RFE.r"
params.lasso_script    = "${projectDir}/../ftd_diagnosis/sequential/lasso.r"
params.selection       = "${projectDir}/../ftd_diagnosis/parallel/features_selection.r"
params.metrics_script  = "${projectDir}/../ftd_diagnosis/util/process_metrics.r"
params.stability_script = "${projectDir}/../ftd_diagnosis/util/stability.r"

params.svm = "${projectDir}/../ftd_diagnosis/parallel/models/svm.r"
params.rf  = "${projectDir}/../ftd_diagnosis/parallel/models/random_forest.r"
params.knn = "${projectDir}/../ftd_diagnosis/parallel/models/kNN.r"
params.xgb = "${projectDir}/../ftd_diagnosis/parallel/models/XGBoost.r"

params.feat_output       = "/shared_data/nf_output/features"
params.labels            = "/app/data/external/ROI_labels.tsv"
params.demographic_data  = null
params.config            = "${projectDir}/configs/hyperparameters.yaml"
params.env               = "${projectDir}/../.env.example"

// ── Composed parameters ───────────────────────────────────────────────────────
params.experiment_path = "${params.brain_segmenter}/${params.experiment_name}/${params.selection_method}"
params.training_args = "${params.brain_segmenter} ${params.selection_method} ${params.experiment_name}"

workflow {
    merge_ch = channel
        .fromPath(params.merge_script)
    
    rfe_ch = channel
        .fromPath(params.rfe_script)
    
    lasso_ch = channel
        .fromPath(params.lasso_script)
    
    labels_file_ch = channel
        .fromPath(params.labels)
    
    // Dati demografici opzionali: se non forniti, viene passato un valore sentinella
    // che merge_radiomics.r interpreta come assenza di covariate demografiche.
    demographic_ch = params.demographic_data
        ? channel.fromPath(params.demographic_data)
        : channel.value("NULL")

    csv_dir = channel
        .fromPath(
            params.feat_output,
            type: 'dir'
        )
    env_ch = channel
        .fromPath(params.env)
    
    hyperparams_ch = channel
            .fromPath(params.config)

    parallel_ch = channel
        .fromPath(params.selection)

    models_ch = channel
        .fromPath([
            params.svm,
            params.rf,
            params.knn,
            params.xgb
        ])
    
    metrics_ch = channel
        .fromPath(params.metrics_script)

    stability_ch = channel
        .fromPath(params.stability_script)


    // Training pipeline
    feat_all = aggregate_features(
        merge_ch, 
        csv_dir,
        labels_file_ch,
        demographic_ch
        )
    if (params.parallel_training) {
        features = select_features(
            parallel_ch,
            feat_all,
            hyperparams_ch
            )
        frequency_stability(
            stability_ch,
            features.feat,
            labels_file_ch
            )
        training_input = features.rds
            .combine(models_ch).combine(env_ch)
        results = parallel_training(
            training_input
            )
        aggregate_metrics(
            results.collect(),
            metrics_ch
            )
    } else {
        sequential_ch = params.selection_method == "rfe" ? rfe_ch :
                        params.selection_method == "lasso" ? lasso_ch:
                        error("Wrong method specified. Use 'rfe' or 'lasso'")
        results = sequential_training(
            feat_all, 
            sequential_ch, 
            hyperparams_ch
            )
        frequency_stability(
            stability_ch, 
            results.feat, 
            labels_file_ch
            )
        csv = results.svm
                .mix(results.rf, 
                     results.knn, 
                     results.xgb
                     )
        aggregate_metrics(
            csv.collect(), 
            metrics_ch
            )
    }
}

process aggregate_features {
    container 'ftd-training'
    debug true

    input:
    path script
    path csv_dir
    path labels
    val  demograph   // "NULL" quando non fornito, path stringa altrimenti

    output:
    path csv_dir

    script:
    """
    Rscript $script $csv_dir $labels "$params.sperimental" "$params.control" $demograph
    """
}

process sequential_training {
    container 'ftd-training'
    publishDir "data/experiments-sequential/${params.experiment_path}", mode: 'copy'
    debug true

    input:
    path csv_dir
    path script
    path config

    output:
    path ("*+SVM.csv"), emit: svm
    path ("*+RF.csv"), emit: rf
    path ("*+kNN.csv"), emit: knn
    path ("*+XGB.csv"), emit: xgb
    path ("*_feat.csv"), emit: feat

    script:
    """
    Rscript $script $csv_dir $config
    """
}

process select_features {
    container 'ftd-training'
    publishDir "data/experiments-selected-mwmote/${params.experiment_path}", mode: 'copy', pattern: 'feat.csv'
    debug true

    input:
    path script
    path csv_dir
    path config

    output:
    tuple path("features", type: 'dir'), path("data", type: 'dir'), emit: rds
    path("feat.csv"), emit: feat

    script:
    """
    Rscript $script $csv_dir ${params.selection_method} $config
    """
}

process parallel_training {
    container 'ftd-training'
    publishDir "data/experiments-selected-mwmote/${params.experiment_path}", mode: 'copy'
    debug true

    input:
    tuple path(feat_dir), path(data_dir), path(script), path(env)

    output:
    path ("*.csv")

    script:
    """
    Rscript $script $data_dir $feat_dir ${params.training_args}
    """
}

process frequency_stability {
    container 'ftd-training'
    debug true
    publishDir (
        params.parallel_training ? 
        "data/experiments-selected-mwmote/${params.experiment_path}" :
        "data/experiments-sequential/${params.experiment_path}",
        mode: 'copy'
    )

    input:
    path script
    path feat
    path roi_id

    output:
    path("frequency.csv")
    path("stability.csv")

    script:
    """
    Rscript $script $feat $roi_id
    """
}

process aggregate_metrics {
    container 'ftd-training'
    debug true
    publishDir (
        params.parallel_training ? 
        "data/experiments-selected-mwmote/${params.experiment_path}" :
        "data/experiments-sequential/${params.experiment_path}",
        mode: 'copy'
    )

    input:
    path csv_files
    path metrics_script

    output:
    path("metrics.csv")

    script:
    """
    Rscript $metrics_script .
    """
}