args <- commandArgs(trailingOnly = TRUE)

input_dir <- args[1]
file_list <- list.files(path = input_dir, pattern = "\\.csv$", full.names = TRUE)

valid_files <- file_list[!grepl("feat|metrics", basename(file_list))]

results <- list()
for (file in valid_files) {
  data <- tryCatch(read.csv(file, header = TRUE), error = function(e) NULL)

  if (!is.null(data) && ncol(data) >= 4) {
    acc  <- as.numeric(data[[1]])
    sens <- as.numeric(data[[2]])
    spec <- as.numeric(data[[3]])
    auc  <- as.numeric(data[[4]])

    row <- c(
      sprintf("%.3f ± %.3f", mean(acc,  na.rm = TRUE), sd(acc,  na.rm = TRUE)),
      sprintf("%.3f ± %.3f", mean(sens, na.rm = TRUE), sd(sens, na.rm = TRUE)),
      sprintf("%.3f ± %.3f", mean(spec, na.rm = TRUE), sd(spec, na.rm = TRUE)),
      sprintf("%.3f ± %.3f", mean(auc,  na.rm = TRUE), sd(auc,  na.rm = TRUE))
    )

    model_name <- tools::file_path_sans_ext(basename(file))
    results[[length(results) + 1]] <- c(model_name, row)
  } else {
    cat(sprintf("Skipping file: %s - invalid format\n", file))
  }
}

if (length(results) > 0) {
  df <- as.data.frame(do.call(rbind, results), stringsAsFactors = FALSE)
  colnames(df) <- c("Model", "acc", "sens", "spec", "auc")

  write.csv(df, "metrics.csv", row.names = FALSE)
} else {
  cat("No valid file founded.\n")
}
