library(mlr)
library(xgboost)

cat("Reading feat_all.csv...\n")
feat_all <- read.csv("/shared_data/nf_output/features/feat_all.csv", check.names=FALSE)
colnames(feat_all)[1] <- "TargetClass"
cat("Rows:", nrow(feat_all), " Cols:", ncol(feat_all), "\n")

# Remove TotalEnergy and near-zero variance columns
total_energy_cols <- grep("original_firstorder_TotalEnergy", names(feat_all), value=TRUE)
feat_all <- feat_all[, !(names(feat_all) %in% total_energy_cols)]

# Select 50 features with highest variance (avoid zero-var cols)
feat_cols_all <- names(feat_all)[names(feat_all) != "TargetClass"]
vars <- sapply(feat_cols_all, function(c) var(feat_all[[c]], na.rm=TRUE))
feat_cols <- names(sort(vars, decreasing=TRUE))[1:min(50, length(vars))]
cat("Selected", length(feat_cols), "features\n")

train_x <- feat_all[, feat_cols, drop=FALSE]
train_y <- factor(feat_all$TargetClass, levels=c(0,1))
train_df <- cbind(data.frame(TargetClass=train_y), train_x)

trainTask <- mlr::makeClassifTask(data=train_df, target="TargetClass", positive="1")
learner <- mlr::makeLearner("classif.xgboost", predict.type="prob",
  par.vals=list(
    objective="binary:logistic",
    eval_metric="error",
    nrounds=50,
    max_depth=3,
    eta=0.3,
    nthread=2
  )
)
cat("Training XGBoost...\n")
xgb_model <- mlr::train(learner, trainTask)
cat("Training done\n")

pred <- predict(xgb_model, newdata=train_x[1,,drop=FALSE])
cat("Sample prediction:", as.character(pred$data$response), "\n")

training_with_outcome <- train_x
training_with_outcome$.outcome <- factor(
  ifelse(as.character(train_y)=="1","bvFTD","HC"),
  levels=c("HC","bvFTD")
)

extended_model <- list(
  trainingData = training_with_outcome,
  x            = as.matrix(train_x),
  y            = training_with_outcome$.outcome,
  mlr_model    = xgb_model,
  booster      = xgb_model$learner.model
)

out_path <- "/shared_data/training_output/xgb.rds"
saveRDS(extended_model, out_path)
cat("Model saved to", out_path, "\n")
cat("booster class:", class(extended_model$booster), "\n")
cat("y levels:", paste(levels(extended_model$y), collapse=", "), "\n")
cat("training rows:", nrow(extended_model$trainingData), "\n")
cat("training cols:", ncol(extended_model$trainingData), "\n")