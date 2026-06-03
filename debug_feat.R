path_features <- "/shared_data/nf_output/features"
labels <- "/shared_data/ROI_labels.tsv"
roi <- read.table(labels, header=TRUE, sep="\t")
cat("ROI rows:", nrow(roi), "\n")
for(j in 1:78) {
  fname <- file.path(path_features, paste0(roi$Label[j], "_feat.csv"))
  if(!file.exists(fname)) { cat("MISSING:", fname, "\n"); next }
  df <- read.csv(fname, check.names=FALSE)
  if(ncol(df) != 126) cat("ROI", j, roi$Label[j], "cols:", ncol(df), "\n")
}
cat("Done\n")