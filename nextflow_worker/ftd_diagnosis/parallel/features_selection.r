library(glmnet)
library(caret)
library(randomForest)
library(cvTools)
library(yaml)
library(imbalance)

#' Data loader
#'
#' @param path_features path string  
data_loader <- function(path_features) {
  all_feat <- read.csv(file = paste(path_features, '/', 'feat_all.csv', sep = ""))
  colnames(all_feat)[1] <- c("TargetClass")
  
  # Remove TotalEnergy columns
  total_energy_cols <- grep("^original_firstorder_TotalEnergy", names(all_feat), value = TRUE)
  all_feat <- all_feat[ , !(names(all_feat) %in% total_energy_cols)]

  all_feat$TargetClass <- as.factor(all_feat$TargetClass)
  return(all_feat)
}


#' Load hyperparameters from config file
#'
#' @param config_path path to the config file
#' @return list with hyperparameters
load_hyperparameters <- function(config_path) {
  if (!file.exists(config_path)) {
    stop(paste("Config file not found:", config_path))
  }

  params <- yaml::read_yaml(config_path)
  return(params)
}


#' LASSO feature selection
#'
#' @param train_data training data.frame
#' @param target_col name of the target class column
#' @return selected feature names
lasso <- function(train_data, params, target_col = "TargetClass") {
  target_idx <- which(names(train_data) == target_col)
  x_train <- data.matrix(train_data[, -target_idx])
  y_train <- as.factor(train_data[, target_idx])

  lasso <- params$selection$lasso
  cvfit <- cv.glmnet(x_train, y_train, family = lasso$family, 
                     lambda = seq(from = lasso$lambda_from, to = lasso$lambda_to, by = lasso$lambda_step), 
                     parallel = lasso$parallel, grouped = lasso$grouped, 
                     type.measure = lasso$type_measure, nfold = lasso$nfold)
  
  while (length(rownames(coef(cvfit, s = lasso$s))[coef(cvfit, s = lasso$s)[,1] != 0][-1]) == 0) {
    cvfit <- cv.glmnet(x_train, y_train, family = lasso$family, 
                       lambda = seq(from = lasso$lambda_from, to = lasso$lambda_to, by = lasso$lambda_step), 
                       parallel = lasso$parallel, grouped = lasso$grouped, 
                       type.measure = lasso$type_measure, nfold = lasso$nfold)
  }
  
  selected_features <- rownames(coef(cvfit, s = lasso$s))[coef(cvfit, s = lasso$s)[,1] != 0][-1]
  return(selected_features)
}


#' RFE feature selection
#'
#' @param train_data training data.frame
#' @param target_col name of the target class column
#' @return selected feature names
rfe <- function(train_data, params, target_col = "TargetClass") {
  target_idx <- which(names(train_data) == target_col)
  x_train <- train_data[, -target_idx]
  y_train <- train_data[, target_idx]
  
  rfe <- params$selection$rfe
  control <- rfeControl(functions = rfFuncs, method = rfe$cv_method, repeats = rfe$cv_repeats, number = rfe$number)
  max_features <- sqrt(nrow(train_data))
  
  results <- caret::rfe(x_train, y_train, sizes = (rfe$min_features:max_features), rfeControl = control)
  
  if (length(predictors(results)) > max_features) {
    feat_idx <- which.max(results$results$Accuracy[1:max_features])
    selected_features <- predictors(results)[1:feat_idx]
  } else {
    selected_features <- predictors(results)
  }
  
  return(selected_features)
}

#' MAIN FUNCTION
#'
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  path_features <- args[1]
  method <- args[2]
  config <- args[3]
  
  params <- load_hyperparameters(config)
  all_feat <- data_loader(path_features)
  
  if (!("TargetClass" %in% colnames(all_feat))) {
      stop("Missing 'TargetClass' column")
  }

  dir.create("features", showWarnings = FALSE)
  dir.create("data", showWarnings = FALSE)
  repeated_feat <- NULL
  
  k <- params$nested_cv$outer_folds
  j <- params$nested_cv$inner_folds
  set.seed(params$selection$seed)

  outer_folds <- createFolds(y = as.factor(all_feat[,1]), k = k, list = TRUE, returnTrain = TRUE)
  for (outer_fold in 1:k) {
      for (inner_fold in 1:j) {
          train_idx <- outer_folds[[inner_fold]]
          test_idx  <- setdiff(seq_len(nrow(all_feat)), train_idx)

          train <- all_feat[train_idx, ]
          test  <- all_feat[test_idx, ]

          if (method == "rfe") {
            selected_features <- rfe(train, params)
          } else if (method == "lasso") {
            selected_features <- lasso(train, params)
          } else {
            stop("Wrong method specified. Use 'rfe' or 'lasso'")
          }

          train_sel <- train[ , c("TargetClass", selected_features), drop = FALSE]
          test_sel  <- test[ , c("TargetClass", selected_features), drop = FALSE]

          # Oversampling minority class
          class_counts <- table(train_sel$TargetClass)
          if (length(class_counts) == 2 && class_counts[1] != class_counts[2]) {
            minority_count <- min(class_counts)
            majority_count <- max(class_counts)
            imb <- majority_count - minority_count

            if (imb > 0) {
                sample <- mwmote(train_sel, numInstances = imb, classAttr = "TargetClass", kNoisy = 3)
                train_sel <- rbind(train_sel, sample)
            }
          }

          repeated_feat <- append(repeated_feat, selected_features)

          saveRDS(selected_features, file = sprintf("features/features_out%d_in%d.rds", outer_fold, inner_fold))
          saveRDS(train_sel, file = sprintf("data/train_out%d_in%d.rds", outer_fold, inner_fold))
          saveRDS(test_sel,  file = sprintf("data/test_out%d_in%d.rds", outer_fold, inner_fold))
      }
  }
  saveRDS(params, file = "data/hyperparameters.rds")
  write.csv(repeated_feat, file = "./feat.csv", row.names = FALSE)
}

if (!interactive()) {
  main()
}