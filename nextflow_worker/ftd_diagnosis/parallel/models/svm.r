library(e1071)
library(caret)
library(ROCit)
library(dplyr)
library(mlflow)

SVM_trainer <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    data_path <- args[1]
    feat_path <- args[2]

    # Experiment info
    segmenter <- args[3]
    selection <- args[4]
    experiment <- args[5]

    svm <- NULL
    fold_info <- list()

    acc_svm <- NULL
    sens_svm <- NULL
    spec_svm <- NULL
    auc_svm <- NULL

    # MLflow configs
    user <- Sys.getenv("MLFLOW_TRACKING_USERNAME")
    token <- Sys.getenv("MLFLOW_TRACKING_PASSWORD")
    uri <- Sys.getenv("MLFLOW_TRACKING_URI")

    mlflow <- tryCatch({
        Sys.setenv(MLFLOW_TRACKING_USERNAME = user)
        Sys.setenv(MLFLOW_TRACKING_PASSWORD = token)
        mlflow_set_tracking_uri(uri)

        info <- tryCatch({
            mlflow_get_experiment(name = experiment)
        }, error = function(e) NULL)

        if (is.null(info)) {
            mlflow_create_experiment(name = experiment)
        }

        mlflow_set_experiment(experiment_name = experiment)
        TRUE
    }, error = function(e) {
        print("Impossible tracking: check MLflow config params!")
        FALSE
    })

    if (mlflow) {
        run <- mlflow_start_run()
        mlflow_set_tag("model", "SVM")
        mlflow_set_tag("brain_segmenter", segmenter)
        mlflow_set_tag("selection_method", selection)
    }

    params  <- readRDS(file.path(data_path, "hyperparameters.rds"))

    k <- params$nested_cv$outer_folds
    j <- params$nested_cv$inner_folds
    set.seed(params$selection$seed)

    fold_counter <- 1
    for (outer_fold in 1:k) {
        for (inner_fold in 1:j) {
            train_sel <- readRDS(file.path(data_path, sprintf("train_out%d_in%d.rds", outer_fold, inner_fold)))
            test_sel  <- readRDS(file.path(data_path, sprintf("test_out%d_in%d.rds", outer_fold, inner_fold)))
            features  <- readRDS(file.path(feat_path, sprintf("features_out%d_in%d.rds", outer_fold, inner_fold)))

            train_x <- train_sel[, !names(train_sel) %in% "TargetClass", drop = FALSE]
            train_y <- as.factor(train_sel$TargetClass)
            test_x <- test_sel[, !names(test_sel) %in% "TargetClass", drop = FALSE]
            test_y <- as.factor(test_sel$TargetClass)

            tuned_svm = tune.svm(train_x, train_y, gamma=params$svm$gamma_values, cost=params$svm$cost_values, tunecontrol=tune.control(cross=params$svm$cross), probability = TRUE)

            fold_info[[fold_counter]] <- tuned_svm
            fold_counter <- fold_counter + 1

            svmfit = tuned_svm$best.model
            prediction <- predict(svmfit, test_x)
            prova <- confusionMatrix(prediction, test_y, positive = '1')
            acc_svm[inner_fold] <- prova$byClass[11]
            sens_svm[inner_fold] <- prova$byClass[1]
            spec_svm[inner_fold] <- prova$byClass[2]

            prediction_prob <- predict(svmfit, test_x, decision.values = TRUE, probability = TRUE)
            roc_emp <- rocit(as.numeric(attr(prediction_prob,'probabilities')[,1]), test_y, negref = '0')
            auc <- ciAUC(roc_emp)
            auc_svm[inner_fold] <- auc$AUC

        }
        to_save_svm <- cbind(acc_svm,sens_svm,spec_svm,auc_svm)
        svm <- rbind(svm, to_save_svm)
    }
    write.csv(svm, file = "./SVM.csv", row.names = FALSE)

    if (mlflow) {
        acc <- mean(svm[, "acc_svm"], na.rm = TRUE)
        sd_acc <- sd(svm[, "acc_svm"], na.rm = TRUE)
        
        sens <- mean(svm[, "sens_svm"], na.rm = TRUE)
        sd_sens <- sd(svm[, "sens_svm"], na.rm = TRUE)
        
        spec <- mean(svm[, "spec_svm"], na.rm = TRUE)
        sd_spec <- sd(svm[, "spec_svm"], na.rm = TRUE)
        
        auc <- mean(svm[, "auc_svm"], na.rm = TRUE)
        sd_auc <- sd(svm[, "auc_svm"], na.rm = TRUE)
        
        max_pos <- which.max(svm[, "acc_svm"])
        tuned_svm <- fold_info[[max_pos]]
        mlflow_log_param("best_gamma", tuned_svm$best.parameters$gamma[[1]])
        mlflow_log_param("best_cost", tuned_svm$best.parameters$cost[[1]])

        mlflow_log_param("gamma_values", paste0("[", paste(params$svm$gamma_values, collapse = ", "), "]"))
        mlflow_log_param("cost_values", paste0("[", paste(params$svm$cost_values, collapse = ", "), "]"))
        mlflow_log_param("cross", params$svm$cross)

        if (selection == "lasso") {
            lasso <- params$selection$lasso
            for (param_name in names(lasso)) {
                mlflow_log_param(paste0("lasso_", param_name), lasso[[param_name]])
            }

        } else if (selection == "rfe") {
            rfe <- params$selection$rfe
            for (param_name in names(rfe)) {
                mlflow_log_param(paste0("rfe_", param_name), rfe[[param_name]])
            }
        }

        mlflow_log_metric("accuracy", acc)
        mlflow_log_metric("sd_accuracy", sd_acc)
        
        mlflow_log_metric("sensitivity", sens)
        mlflow_log_metric("sd_sensitivity", sd_sens)
        
        mlflow_log_metric("specificity", spec)
        mlflow_log_metric("sd_specificity", sd_spec)
        
        mlflow_log_metric("auc", auc)
        mlflow_log_metric("sd_auc", sd_auc)
        
        saveRDS(tuned_svm$finalModel, "svm.rds")
        mlflow_log_artifact("svm.rds", "model")
        mlflow_log_artifact("svm.csv", "folds_eval")

        mlflow_end_run()
    }
}

if (!interactive()) {
  SVM_trainer()
}
