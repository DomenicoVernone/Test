args_parser <- function(x) {
  x <- gsub("\\[|\\]", "", x)
  x <- gsub(" ", "", x)
  items <- unlist(strsplit(x, ","))
  return(items)
}

get_all_feat <- function(groups_list, class, demograph) {
    all_feat <- data.frame()
    roi <- read.table(file.path(labels), header = FALSE, sep = "")

    for (group in groups_list) {
        
        subset <- data.frame(TargetClass = class)
        for (j in c(1:78)) {
            feat_roi <- read.csv(file.path(path_features, paste(roi$V3[j],'_feat.csv',sep='')))
            if (is.null(demograph)) {
                subset_roi <- feat_roi[grepl(group, feat_roi$Image), ]
            } else {
                filter <- feat_roi[grepl(group, feat_roi$Image), ]
                to_keep <- sapply(filter$Image, function(x) {
                    any(sapply(demograph$SUB, function(sub) {
                        grepl(sub, x, fixed = TRUE)
                    }))
                })
                subset_roi <- filter[to_keep, ]
            }
            matrix <- subset_roi[,39:126]
            subset <- cbind(subset, matrix)
        }

        all_feat <- rbind(all_feat, subset)
    }
    return(all_feat)
}

args <- commandArgs(trailingOnly = TRUE)
path_features <- args[1]
labels <- args[2]

sperimental <- args_parser(args[3])  # Sperimental group
control <- args_parser(args[4])      # Control group

path_csv <- args[5]

demograph <- NULL
if (path_csv != "NULL") {
    demograph <- read.csv(path_csv)
}

# Sperimental group
sperimental_feat <- get_all_feat(sperimental, 1, demograph)
write.csv(sperimental_feat,file=paste(path_features,'/','sperimental_feat_all.csv',sep=""), row.names = FALSE)

# Control group
control_feat <- get_all_feat(control, 0, demograph)
write.csv(control_feat,file=paste(path_features,'/','control_feat_all.csv',sep=""), row.names = FALSE)

feat_all <- rbind(sperimental_feat, control_feat)

# Features files
write.csv(feat_all,file=paste(path_features,'/','feat_all.csv',sep=""), row.names = FALSE)