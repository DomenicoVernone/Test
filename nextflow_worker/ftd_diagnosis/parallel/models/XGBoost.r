library(mlr)
library(xgboost)
library(caret)
library(ROCit)
library(mlflow)

XGBoost_trainer <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    data_path <- args[1]
    feat_path <- args[2]

    # Experiment info
    segmenter <- args[3]
    selection <- args[4]
    experiment <- args[5]

    xgb <- NULL
    fold_info <- list()
    fold_model <- list()

    acc_xgb <- NULL
    sens_xgb <- NULL
    spec_xgb <- NULL
    auc_xgb <- NULL

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
        mlflow_set_tag("model", "XGBoost")
        mlflow_set_tag("brain_segmenter", segmenter)
        mlflow_set_tag("selection_method", selection)
    }

    params  <- readRDS(file.path(data_path, "hyperparameters.rds"))
    tuning <- params$xgboost$tuning_ranges

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
            train_y <- factor(train_sel$TargetClass, levels = c(0, 1))
            test_x  <- test_sel[, !names(test_sel) %in% "TargetClass", drop = FALSE]
            test_y  <- factor(test_sel$TargetClass, levels = c(0, 1))

            train_df <- cbind(train_y, train_x)
            colnames(train_df)[1] <- "TargetClass"
            test_df  <- cbind(test_y, test_x)
            colnames(test_df)[1] <- "TargetClass"

            trainTask <- makeClassifTask(data = train_df, target = "TargetClass", positive = "1")
            testTask  <- makeClassifTask(data = test_df, target = "TargetClass")

            # Hyperparameter tuning
            xgb_learner <- makeLearner(
                "classif.xgboost",
                predict.type = "prob",
                par.vals = list(
                    objective = params$xgboost$objective,
                    eval_metric = params$xgboost$eval_metric,
                    nrounds = params$xgboost$nrounds,
                    nthread = params$xgboost$nthread
                )
            )

            xgb_params <- makeParamSet(
                makeIntegerParam("nrounds", lower = tuning$nrounds_min, upper = tuning$nrounds_max),
                makeIntegerParam("max_depth", lower = tuning$max_depth_min, upper = tuning$max_depth_max),
                makeNumericParam("eta", lower = tuning$eta_min, upper = tuning$eta_max),
                makeNumericParam("lambda", lower = tuning$lambda_min, upper = tuning$lambda_max)
            )

            control <- makeTuneControlRandom(maxit = 1)
            resample_desc <- makeResampleDesc("CV", iters = 10)

            tuned_params <- tuneParams(
                learner = xgb_learner,
                task = trainTask,
                resampling = resample_desc,
                par.set = xgb_params,
                control = control
            )

            xgb_tuned_learner <- setHyperPars(
                learner = xgb_learner,
                par.vals = tuned_params$x
            )

            # Model training
            xgb_model <- mlr::train(xgb_tuned_learner, trainTask)

            fold_info[[fold_counter]] <- tuned_params
            fold_model[[fold_counter]] <- xgb_model
            fold_counter <- fold_counter + 1

            prediction  <- predict(xgb_model, testTask)
            prova <-  caret::confusionMatrix(prediction$data$response,test_y, positive = '1')
            acc_xgb[inner_fold] <- prova$byClass[11]
            sens_xgb[inner_fold] <- prova$byClass[1]
            spec_xgb[inner_fold] <- prova$byClass[2]
            prediction  <- predict(xgb_model, testTask, decision.values = TRUE,  type = 'prob')
            roc_emp <- rocit(prediction$data$prob.1,test_y, negref = '0')
            auc <- ciAUC(roc_emp)
            auc_xgb[inner_fold] <- auc$AUC

        }
        to_save_xgb <- cbind(acc_xgb,sens_xgb,spec_xgb,auc_xgb)
        xgb <- rbind(xgb, to_save_xgb)
    }
    write.csv(xgb, file = "./xgb.csv", row.names = FALSE)

    if (mlflow) {
        acc <- mean(xgb[, "acc_xgb"], na.rm = TRUE)
        sd_acc <- sd(xgb[, "acc_xgb"], na.rm = TRUE)
        
        sens <- mean(xgb[, "sens_xgb"], na.rm = TRUE)
        sd_sens <- sd(xgb[, "sens_xgb"], na.rm = TRUE)
        
        spec <- mean(xgb[, "spec_xgb"], na.rm = TRUE)
        sd_spec <- sd(xgb[, "spec_xgb"], na.rm = TRUE)
        
        auc <- mean(xgb[, "auc_xgb"], na.rm = TRUE)
        sd_auc <- sd(xgb[, "auc_xgb"], na.rm = TRUE)
        
        max_pos <- which.max(xgb[, "acc_xgb"])
        xgb_model <- fold_model[[max_pos]]
        tuned_params <- fold_info[[max_pos]]

        best_params <- tuned_params$x
        for (param_name in names(best_params)) {
            mlflow_log_param(paste0("best_", param_name), best_params[[param_name]])
        }

        for (param_name in names(params$xgboost$tuning_ranges)) {
            mlflow_log_param(param_name, params$xgboost$tuning_ranges[[param_name]])
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
        
        saveRDS(xgb_model, "xgb.rds")
        mlflow_log_artifact("xgb.rds", "model")
        mlflow_log_artifact("xgb.csv", "folds_eval")

        mlflow_end_run()
    }
}

if (!interactive()) {
  XGBoost_trainer()
}