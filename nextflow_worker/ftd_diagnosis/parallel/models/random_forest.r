library(randomForest)
library(e1071)
library(caret)
library(ROCit)
library(mlflow)

RF_trainer <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    data_path <- args[1]
    feat_path <- args[2]

    # Experiment info
    segmenter <- args[3]
    selection <- args[4]
    experiment <- args[5]
 
    rf <- NULL
    fold_info <- list()

    acc_rf <- NULL
    sens_rf <- NULL
    spec_rf <- NULL
    auc_rf <- NULL

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
        mlflow_set_tag("model", "random forest")
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

            feat <- round(sqrt(ncol(train_sel)))
            mtry_vals <- 1:feat
            tuned_RF = tune.randomForest(train_x, train_y, mtry = mtry_vals, ntree = params$rf$ntree_options, tunecontrol=tune.control(cross=params$rf$cross),probability = TRUE)

            fold_info[[fold_counter]] <- tuned_RF
            fold_counter <- fold_counter + 1

            rffit = tuned_RF$best.model
            prediction <- predict(rffit, test_x)
            prova <- confusionMatrix(prediction, test_y, positive = '1')
            acc_rf[inner_fold] <- prova$byClass[11]
            sens_rf[inner_fold] <- prova$byClass[1]
            spec_rf[inner_fold] <- prova$byClass[2]

            prediction <- predict(rffit, test_x, type = "prob")
            roc_emp <- rocit(prediction[,2], test_y, negref = '0')
            auc <- ciAUC(roc_emp)
            auc_rf[inner_fold] <- auc$AUC

        }
        to_save_rf <- cbind(acc_rf,sens_rf,spec_rf,auc_rf)
        rf <- rbind(rf, to_save_rf)
    }
    write.csv(rf, file = "./rf.csv", row.names = FALSE)

    if (mlflow) {
        acc <- mean(rf[, "acc_rf"], na.rm = TRUE)
        sd_acc <- sd(rf[, "acc_rf"], na.rm = TRUE)
        
        sens <- mean(rf[, "sens_rf"], na.rm = TRUE)
        sd_sens <- sd(rf[, "sens_rf"], na.rm = TRUE)
        
        spec <- mean(rf[, "spec_rf"], na.rm = TRUE)
        sd_spec <- sd(rf[, "spec_rf"], na.rm = TRUE)
        
        auc <- mean(rf[, "auc_rf"], na.rm = TRUE)
        sd_auc <- sd(rf[, "auc_rf"], na.rm = TRUE)
        
        max_pos <- which.max(rf[, "acc_rf"])
        tuned_rf <- fold_info[[max_pos]]

        for (param_name in names(tuned_rf$best.parameters)) {
            mlflow_log_param(paste0("best_", param_name), tuned_rf$best.parameters[[param_name]])
        }

        mlflow_log_param("ntree_options", paste0("[", paste(params$rf$ntree_options, collapse = ", "), "]"))
        mlflow_log_param("cross", params$rf$cross)

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
        
        saveRDS(tuned_rf$finalModel, "rf.rds")
        mlflow_log_artifact("rf.rds", "model")
        mlflow_log_artifact("rf.csv", "folds_eval")
        
        mlflow_end_run()
    }
}

if (!interactive()) {
  RF_trainer()
}
