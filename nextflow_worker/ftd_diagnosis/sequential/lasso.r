library(tidyr)
library(dplyr)
library(glmnet)
library(caret)
library(randomForest)
library(cvTools)
library(yaml)
library(mlr)
library(xgboost)
library(ROCit)
library(e1071)

args <- commandArgs(trailingOnly = TRUE)

path_features <- args[1]
config <- args[2]

all_feat <- read.csv(file=paste(path_features,'/','feat_all.csv',sep=""))
params <- yaml::read_yaml(config)

set.seed(params$selection$seed)

#####################delete total energy
name_tot_energy <- 'original_firstorder_TotalEnergy'

for (i in c(1:77)) {
  name_tot_energy <- append(name_tot_energy,paste0('original_firstorder_TotalEnergy.',i))
}

all_feat <- all_feat[ , -which(names(all_feat) %in% name_tot_energy)]
colnames(all_feat)[1] <- 'TargetClass'

all_feat$TargetClass <- as.factor(all_feat$TargetClass)

##################LASSO
k <- params$nested_cv$outer_folds
j <- params$nested_cv$inner_folds

folds <- cvFolds(NROW(all_feat), K=k)
acc_svm <- NULL
acc_rf <- NULL
acc_knn <- NULL
acc_xgb <- NULL

sens_svm <- NULL
sens_rf <- NULL
sens_knn <- NULL
sens_xgb <- NULL

spec_svm <- NULL
spec_rf <- NULL
spec_knn <- NULL
spec_xgb <- NULL

auc_svm <- NULL
auc_rf <- NULL
auc_knn <- NULL
auc_xgb <- NULL

repeated_perf_svm <- NULL
repeated_perf_rf <- NULL
repeated_perf_knn <- NULL
repeated_perf_xgb <- NULL

svm <- NULL
rf <- NULL
knn <- NULL
xgb <- NULL

repeated_feat <- NULL
for (iter in 1:k) {
  features <- NULL
  for(i in 1:j){
    train <- all_feat[folds$subsets[folds$which != i], ] #Set the training set
    test <- all_feat[folds$subsets[folds$which == i], ] #Set the validation set
    model <- glmnet(data.matrix(train[,-1]), as.factor(train[,1]), family=params$selection$lasso$family, alpha = 1)

    cvfit=cv.glmnet(data.matrix(train[,-1]),
                    as.factor(train[,1]),
                    family=params$selection$lasso$family,
                    lambda = seq(from=params$selection$lasso$lambda_from,
                                 to=params$selection$lasso$lambda_to,
                                 by=params$selection$lasso$lambda_step),
                    parallel = params$selection$lasso$parallel,
                    grouped=params$selection$lasso$grouped,
                    type.measure = params$selection$lasso$type_measure,
                    nfolds = params$selection$lasso$nfold)

    while (length(rownames(coef(cvfit, s = params$selection$lasso$s))[coef(cvfit, s = params$selection$lasso$s)[,1]!= 0][-1]) == 0) {
      cvfit=cv.glmnet(data.matrix(train[,-1]),
                      as.factor(train[,1]),
                      family=params$selection$lasso$family,
                      lambda = seq(from=params$selection$lasso$lambda_from,
                                   to=params$selection$lasso$lambda_to,
                                   by=params$selection$lasso$lambda_step),
                      parallel = params$selection$lasso$parallel,
                      grouped=params$selection$lasso$grouped,
                      type.measure = params$selection$lasso$type_measure,
                      nfolds = params$selection$lasso$nfold)
    }

    features <- append(features,
                       rownames(coef(cvfit, s = params$selection$lasso$s))[coef(cvfit, s = params$selection$lasso$s)[,1]!= 0][-1],
                       after = length(features))

    train_sel <- train[rownames(coef(cvfit, s = params$selection$lasso$s))[coef(cvfit, s = params$selection$lasso$s)[,1]!= 0][-1]]
    test_sel <- test[rownames(coef(cvfit, s = params$selection$lasso$s))[coef(cvfit, s = params$selection$lasso$s)[,1]!= 0][-1]]

    #####SVM
    tuned_svm = tune.svm(train_sel,
                         as.factor(train[,1]),
                         gamma=params$svm$gamma_values,
                         cost=params$svm$cost_values,
                         tunecontrol=tune.control(cross=params$svm$cross),
                         probability = TRUE)

    svmfit = tuned_svm$best.model
    prediction  <- predict(svmfit, test_sel)
    prova <- confusionMatrix(prediction,as.factor(test[,1]), positive = '1')
    acc_svm[i] <- prova$byClass[11]
    sens_svm[i] <- prova$byClass[1]
    spec_svm[i] <- prova$byClass[2]
    prediction  <- predict(svmfit, test_sel, decision.values = TRUE, probability = TRUE)
    roc_emp <- rocit(as.numeric(attr(prediction,'probabilities')[,1]),factor(test[,1]), negref = '0')
    auc <- ciAUC(roc_emp)
    auc_svm[i] <- auc$AUC

    #####RF
    tuned_RF = tune.randomForest(train_sel,
                                 as.factor(train[,1]),
                                 mtry = c(1:5),
                                 ntree = params$rf$ntree_options,
                                 tunecontrol=tune.control(cross=params$rf$cross),
                                 probability = TRUE)

    rffit = tuned_RF$best.model
    prediction  <- predict(rffit, test_sel)
    prova <- confusionMatrix(prediction,as.factor(test[,1]), positive = '1')
    acc_rf[i] <- prova$byClass[11]
    sens_rf[i] <- prova$byClass[1]
    spec_rf[i] <- prova$byClass[2]
    prediction  <- predict(rffit, test_sel, decision.values = TRUE,  type = 'prob')
    roc_emp <- rocit(prediction[,2],factor(test[,1]), negref = '0')
    auc <- ciAUC(roc_emp)
    auc_rf[i] <- auc$AUC

    #########kNN
    training_control <- trainControl(method = params$knn$cv_method,
                                     summaryFunction = defaultSummary,
                                     classProbs = TRUE,
                                     number = params$knn$cv_number,
                                     repeats = params$knn$cv_repeats)

    class <- NULL
    for (z in 1:dim(train)[1]) {
      if (train[z,1] == 0) {
        class[z] <- 'control'
      } else {
        class[z] <- 'sperimental'
      }
    }

    tuned_knn <- caret::train(train_sel,
                              as.factor(class),
                              method = "knn",
                              trControl = training_control,
                              tuneGrid = data.frame(k = seq(params$knn$k_min,
                                                            params$knn$k_max,
                                                            by = params$knn$k_step)))

    knn_predictions <- predict(tuned_knn, newdata = test_sel, type = "prob")
    class = ifelse(knn_predictions$sperimental > params$knn$probability_threshold, "sperimental", "control")
    class = factor(class)
    class_test <- NULL
    for (z in 1:dim(test)[1]) {
      if (test[z,1] == 0) {
        class_test[z] <- 'control'
      } else {
        class_test[z] <- 'sperimental'
      }
    }

    prova <- confusionMatrix(class,as.factor(class_test), positive = 'sperimental')
    acc_knn[i] <- prova$byClass[11]
    sens_knn[i] <- prova$byClass[1]
    spec_knn[i] <- prova$byClass[2]
    roc_emp <- rocit(knn_predictions[,2],factor(class_test), negref = "control")
    auc <- ciAUC(roc_emp)
    auc_knn[i] <- auc$AUC

    ###########XGBoost
    train <- cbind(train$TargetClass,train_sel)
    colnames(train)[1] <- "TargetClass"
    test <- cbind(test$TargetClass,test_sel)
    colnames(test)[1] <- "TargetClass"
    trainTask <- makeClassifTask(data = train, target = "TargetClass", positive = 1)
    testTask <- makeClassifTask(data = test, target = "TargetClass")

    xgb_learner <- makeLearner(
      "classif.xgboost",
      predict.type = "prob",
      par.vals = list(
        objective = params$xgboost$objective,
        eval_metric = params$xgboost$eval_metric,
        nthread = params$xgboost$nthread,
        nrounds = params$xgboost$nrounds
      )
    )

    xgb_params <- makeParamSet(
      makeIntegerParam("nrounds", lower = params$xgboost$tuning_ranges$nrounds_min,
                                     upper = params$xgboost$tuning_ranges$nrounds_max),
      makeIntegerParam("max_depth", lower = params$xgboost$tuning_ranges$max_depth_min,
                                      upper = params$xgboost$tuning_ranges$max_depth_max),
      makeNumericParam("eta", lower = params$xgboost$tuning_ranges$eta_min,
                                  upper = params$xgboost$tuning_ranges$eta_max),
      makeNumericParam("lambda", lower = params$xgboost$tuning_ranges$lambda_min,
                                     upper = params$xgboost$tuning_ranges$lambda_max)
    )

    control <- makeTuneControlRandom(maxit = params$xgboost$tuning_iterations)
    resample_desc <- makeResampleDesc("CV", iters = params$nested_cv$inner_folds)

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

    xgb_model <- train(xgb_tuned_learner, trainTask)
    prediction  <- predict(xgb_model, testTask)
    prova <- confusionMatrix(prediction$data$response,as.factor(test[,1]), positive = '1')
    acc_xgb[i] <- prova$byClass[11]
    sens_xgb[i] <- prova$byClass[1]
    spec_xgb[i] <- prova$byClass[2]
    prediction  <- predict(xgb_model, testTask, decision.values = TRUE,  type = 'prob')
    roc_emp <- rocit(prediction$data$prob.1,factor(test[,1]), negref = '0')
    auc <- ciAUC(roc_emp)
    auc_xgb[i] <- auc$AUC

  }

  to_save_svm <- cbind(acc_svm,sens_svm,spec_svm,auc_svm)
  to_save_rf <- cbind(acc_rf,sens_rf,spec_rf,auc_rf)
  to_save_knn <- cbind(acc_knn,sens_knn,spec_knn,auc_knn)
  to_save_xgb <- cbind(acc_xgb,sens_xgb,spec_xgb,auc_xgb)

  repeated_perf_svm <- rbind(repeated_perf_svm, colMeans(to_save_svm))
  repeated_perf_rf <- rbind(repeated_perf_rf, colMeans(to_save_rf))
  repeated_perf_knn <- rbind(repeated_perf_knn, colMeans(to_save_knn))
  repeated_perf_xgb <- rbind(repeated_perf_xgb, colMeans(to_save_xgb))

  repeated_feat <- append(repeated_feat,features)

  svm <- rbind(svm, to_save_svm)
  rf <- rbind(rf, to_save_rf)
  knn <- rbind(knn, to_save_knn)
  xgb <- rbind(xgb, to_save_xgb)
}

write.csv(svm, file = "./LASSO+SVM.csv", row.names = FALSE)
write.csv(rf, file = "./LASSO+RF.csv", row.names = FALSE)
write.csv(knn, file = "./LASSO+kNN.csv", row.names = FALSE)
write.csv(xgb, file = "./LASSO+XGB.csv", row.names = FALSE)
write.csv(repeated_feat, file = "./LASSO_feat.csv", row.names = FALSE)
