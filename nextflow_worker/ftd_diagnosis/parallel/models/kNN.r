library(caret)
library(ROCit)
library(e1071)
library(mlflow)

kNN_trainer <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    data_path <- args[1]
    feat_path <- args[2]

    # Experiment info
    segmenter <- args[3]
    selection <- args[4]
    experiment <- args[5]

    knn <- NULL
    fold_info <- list()

    acc_knn <- NULL
    sens_knn <- NULL
    spec_knn <- NULL
    auc_knn <- NULL

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
        mlflow_set_tag("model", "kNN")
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

            training_control <- trainControl(method = params$knn$cv_method,
                                     summaryFunction = defaultSummary,
                                     classProbs = TRUE,
                                     number = params$knn$cv_number,
                                     repeats = params$knn$cv_repeats)
            class <- NULL
            i <- NULL
            for (i in 1:dim(train_sel)[1]) {
                if (train_sel[i,1] == 0) {
                    class[i] <- 'control'
                } else {
                    class[i] <- 'sperimental'
                }
            }

            tuned_knn <- caret::train(train_x,
                              as.factor(class),
                              method = "knn",
                              trControl = training_control,
                              tuneGrid = data.frame(k = seq(params$knn$k_min,params$knn$k_max,by = params$knn$k_step)))

            fold_info[[fold_counter]] <- tuned_knn
            fold_counter <- fold_counter + 1

            knn_predictions <- predict(tuned_knn, newdata = test_x, type = "prob")

            class = ifelse(knn_predictions$sperimental > params$knn$probability_threshold, "sperimental", "control")
            class = factor(class)

            class_test <- NULL
            i <- NULL
            for (i in 1:dim(test_sel)[1]) {
                if (test_sel[i,1] == 0) {
                    class_test[i] <- 'control'
                } else {
                    class_test[i] <- 'sperimental'
                }
            }
            prova <- confusionMatrix(class,as.factor(class_test), positive = 'sperimental')
            acc_knn[inner_fold] <- prova$byClass[11]
            sens_knn[inner_fold] <- prova$byClass[1]
            spec_knn[inner_fold] <- prova$byClass[2]
            roc_emp <- rocit(knn_predictions[,2],factor(class_test), negref = 'control')
            auc <- ciAUC(roc_emp)
            auc_knn[inner_fold] <- auc$AUC

        }
        to_save_knn <- cbind(acc_knn,sens_knn,spec_knn,auc_knn)
        knn <- rbind(knn, to_save_knn)
    }
    write.csv(knn, file = "./kNN.csv", row.names = FALSE)

    if (mlflow) {
        acc <- mean(knn[, "acc_knn"], na.rm = TRUE)
        sd_acc <- sd(knn[, "acc_knn"], na.rm = TRUE)
        
        sens <- mean(knn[, "sens_knn"], na.rm = TRUE)
        sd_sens <- sd(knn[, "sens_knn"], na.rm = TRUE)
        
        spec <- mean(knn[, "spec_knn"], na.rm = TRUE)
        sd_spec <- sd(knn[, "spec_knn"], na.rm = TRUE)
        
        auc <- mean(knn[, "auc_knn"], na.rm = TRUE)
        sd_auc <- sd(knn[, "auc_knn"], na.rm = TRUE)
        
        max_pos <- which.max(knn[, "acc_knn"])
        tuned_knn <- fold_info[[max_pos]]

        for (param_name in names(tuned_knn$bestTune)) {
            mlflow_log_param(paste0("best_", param_name), tuned_knn$bestTune[[param_name]])
        }

        for (param_name in names(params$knn)) {
            mlflow_log_param(param_name, params$knn[[param_name]])
        }

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
        
        saveRDS(tuned_knn$finalModel, "knn.rds")
        mlflow_log_artifact("knn.rds", "model")
        mlflow_log_artifact("kNN.csv", "folds_eval")

        mlflow_end_run()
    }
}

if (!interactive()) {
  kNN_trainer()
}
