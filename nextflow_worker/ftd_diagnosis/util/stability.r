library(tidyr)
library(dplyr)

compute_freq <- function (x, n) {
  tail(sort(table(unlist(strsplit(as.character(x), ',')))), n)
}

frequency_stability <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  feat_path <- args[1]
  roi_id_path <- args[2]

  feat <- read.csv(feat_path)
  freq <- as.data.frame(compute_freq(feat$x,100))
  quantile <- quantile(freq$Freq) 
  selected <- freq[which(freq$Freq == as.numeric(quantile[5])),'Var1']
  selected <- data.frame(
    X2 = as.character(selected),
    stringsAsFactors = FALSE
   )

  df <- selected %>%
    separate(X2, into = c("Radiomics", "ROI"), sep = "\\.", fill = "right") %>%
    mutate(ROI = ifelse(is.na(ROI), "0", ROI))
  df$ROI <- as.integer(df$ROI)

  roi_id <- read.table(
    roi_id_path,
    sep = "\t",
    header = FALSE,
    col.names = c("ROI", "label", "name")
  )
  join <- df %>%
    left_join(roi_id, by = "ROI")

  write.csv(freq, './frequency.csv')
  write.csv(join, './stability.csv', row.names = FALSE)
}

if (!interactive()) {
  frequency_stability()
}
