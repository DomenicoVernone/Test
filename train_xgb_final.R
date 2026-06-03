library(xgboost)

cat("Reading feat_all.csv...\n")
feat_all <- read.csv("/shared_data/nf_output/features/feat_all.csv", check.names=FALSE)
colnames(feat_all)[1] <- "TargetClass"
cat("Rows:", nrow(feat_all), " Cols:", ncol(feat_all), "\n")

total_energy_cols <- grep("original_firstorder_TotalEnergy", names(feat_all), value=TRUE)
feat_all <- feat_all[, !(names(feat_all) %in% total_energy_cols)]

feat_cols_all <- names(feat_all)[names(feat_all) != "TargetClass"]
vars <- sapply(feat_cols_all, function(c) var(feat_all[[c]], na.rm=TRUE))
feat_cols <- names(sort(vars, decreasing=TRUE))[1:min(50, length(vars))]
cat("Selected", length(feat_cols), "features by variance\n")

train_x <- feat_all[, feat_cols, drop=FALSE]
train_y <- feat_all$TargetClass
labels <- factor(ifelse(train_y == 1, "bvFTD", "HC"), levels=c("HC","bvFTD"))

dmatrix <- xgb.DMatrix(
  data = as.matrix(train_x),
  label = as.numeric(train_y)
)

set.seed(42)
cat("Training xgb.Booster (50 rounds)...\n")
booster <- xgb.train(
  params = list(
    objective   = "binary:logistic",
    eval_metric = "error",
    eta         = 0.3,
    max_depth   = 3,
    nthread     = 2
  ),
  data    = dmatrix,
  nrounds = 50,
  verbose = 0
)

pred_test <- predict(booster, dmatrix)
pred_labels <- ifelse(pred_test > 0.5, "bvFTD", "HC")
acc <- mean(pred_labels == as.character(labels))
cat("Training accuracy:", round(acc, 3), "\n")
cat("Sample prob[1]:", round(pred_test[1], 4), "-> label:", pred_labels[1], "\n")

training_with_outcome <- train_x
training_with_outcome$.outcome <- labels

extended_model <- list(
  trainingData = training_with_outcome,
  x            = as.matrix(train_x),
  y            = labels,
  booster      = booster
)

out_path <- "/shared_data/training_output/xgb_final.rds"
saveRDS(extended_model, out_path)
cat("Model saved to", out_path, "\n")
cat("booster class:", class(extended_model$booster), "\n")
cat("y levels:", paste(levels(extended_model$y), collapse=", "), "\n")
cat("trainingData rows:", nrow(extended_model$trainingData), "\n")
cat("features in model:", length(feat_cols), "\n")