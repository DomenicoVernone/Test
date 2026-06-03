library(caret)
library(randomForest)

cat("Reading feat_all.csv...\n")
feat_all <- read.csv("/shared_data/nf_output/features/feat_all.csv", check.names=FALSE)
colnames(feat_all)[1] <- "TargetClass"
cat("Rows:", nrow(feat_all), " Cols:", ncol(feat_all), "\n")

total_energy_cols <- grep("original_firstorder_TotalEnergy", names(feat_all), value=TRUE)
feat_all <- feat_all[, !(names(feat_all) %in% total_energy_cols)]

feat_cols_all <- names(feat_all)[names(feat_all) != "TargetClass"]
vars <- sapply(feat_cols_all, function(c) var(feat_all[[c]], na.rm=TRUE))
feat_cols <- names(sort(vars, decreasing=TRUE))[1:min(50, length(vars))]
cat("Top-variance features selected:", length(feat_cols), "\n")

feat_all$TargetClass <- factor(
  ifelse(feat_all$TargetClass == 1, "bvFTD", "HC"),
  levels = c("HC","bvFTD")
)

train_df <- feat_all[, c("TargetClass", feat_cols)]

set.seed(42)
ctrl <- trainControl(method="cv", number=3, classProbs=TRUE)
cat("Training Random Forest via caret (3-fold CV, 50 trees)...\n")
rf_model <- train(
  TargetClass ~ .,
  data = train_df,
  method = "rf",
  trControl = ctrl,
  ntree = 50,
  tuneGrid = data.frame(mtry = 5)
)
cat("Training complete\n")
cat("Best accuracy:", max(rf_model$results$Accuracy), "\n")

pred_sample <- predict(rf_model, newdata=train_df[1, feat_cols, drop=FALSE], type="raw")
cat("Sample prediction:", as.character(pred_sample), "\n")
cat("trainingData rows:", nrow(rf_model$trainingData), "\n")
cat(".outcome levels:", paste(levels(rf_model$trainingData$.outcome), collapse=", "), "\n")

out_path <- "/shared_data/training_output/xgb.rds"
saveRDS(rf_model, out_path)
cat("Model saved to", out_path, "\n")
cat("Model class:", paste(class(rf_model), collapse=", "), "\n")