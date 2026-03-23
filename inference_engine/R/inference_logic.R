#' Modulo di Inferenza Clinica e Calcolo Topologico (UMAP)
#'
#' Contiene esclusivamente la logica di business e la matematica.
#' Nessuna dipendenza dal layer web (Plumber).

library(uwot)
library(caret)
library(xgboost)

#' Esegue la pipeline di inferenza e calcola l'UMAP 3D
#' @param task_id ID del task corrente
#' @param model_dir Percorso esatto del file .rds scaricato da MLflow
#' @param csv_file Percorso esatto del file CSV contenente le feature
run_clinical_inference <- function(task_id, model_dir, csv_file) {
  print(paste("🔍 Caricamento del modello esatto da:", model_dir))
  if (!file.exists(model_dir)) {
    stop(paste("File del modello non trovato:", model_dir))
  }

  modello <- readRDS(model_dir)
  dati_paziente <- read.csv(csv_file, check.names = FALSE)
  print("✅ Artefatto R e dati paziente caricati con successo!")

  print("⚙️ Estrazione dati storici dal modello...")
  storico_x <- NULL
  storico_y <- NULL
  feature_req <- NULL

  if (!is.null(modello$trainingData)) {
    storico_x <- modello$trainingData
    if (".outcome" %in% colnames(storico_x)) {
      storico_y <- storico_x$.outcome
      storico_x$.outcome <- NULL
    }
    feature_req <- colnames(storico_x)
  } else if (!is.null(modello$learn$X)) {
    storico_x <- modello$learn$X
    storico_y <- modello$learn$y
    feature_req <- colnames(storico_x)
  } else if (!is.null(modello$x)) {
    storico_x <- as.data.frame(modello$x)
    storico_y <- modello$y
    feature_req <- colnames(storico_x)
  }

  if (is.null(feature_req)) {
    if (!is.null(modello$coefnames)) {
      feature_req <- modello$coefnames
    } else if (!is.null(modello$terms)) {
      feature_req <- attr(modello$terms, "term.labels")
    }
  }

  if (is.null(feature_req)) {
    stop("Impossibile dedurre le feature necessarie dal modello.")
  }

  print("🛡️ Allineamento dimensionale: MAPPING DETERMINISTICO da ROI labels...")

  # Carica le ROI labels nello stesso ordine usato durante il training.
  # Il loop in merge_radiomics.r itera j=1:78 su roi$V3, quindi la prima ROI
  # genera colonne senza suffisso, la seconda aggiunge ".1", la terza ".2", ecc.
  # Il suffisso numerico N corrisponde alla ROI all'indice N+1 nel file labels.
  roi_labels_path <- Sys.getenv("NF_LABELS", unset = "/tmp/ROI_labels.tsv")
  roi_labels <- read.table(roi_labels_path, header = FALSE, sep = "")
  roi_names <- roi_labels$V3  # 78 ROI in ordine

  build_roi_mapping <- function(feature_req, roi_names) {
    mapping <- character(length(feature_req))
    for (i in seq_along(feature_req)) {
      fname <- feature_req[i]
      suffix_match <- regmatches(fname, regexpr("\\.[0-9]+$", fname))
      if (length(suffix_match) == 0 || suffix_match == "") {
        roi_idx <- 1  # nessun suffisso = prima ROI (lh-bankssts)
        base_name <- fname
      } else {
        roi_idx <- as.integer(sub("\\.", "", suffix_match)) + 1
        base_name <- sub("\\.[0-9]+$", "", fname)
      }
      if (roi_idx > length(roi_names)) {
        print(paste("⚠️ Indice ROI fuori range:", roi_idx, "per feature:", fname))
        mapping[i] <- fname
      } else {
        mapping[i] <- paste0(roi_names[roi_idx], "_", base_name)
      }
    }
    return(mapping)
  }

  csv_column_names <- build_roi_mapping(feature_req, roi_names)

  dati_nuovo <- data.frame(matrix(0, nrow = 1, ncol = length(feature_req)))
  colnames(dati_nuovo) <- feature_req

  for (i in seq_along(feature_req)) {
    csv_col <- csv_column_names[i]
    if (csv_col %in% colnames(dati_paziente)) {
      val <- as.numeric(dati_paziente[1, csv_col])
      dati_nuovo[1, i] <- ifelse(is.na(val), 0, val)
    } else {
      print(paste("⚠️ Colonna non trovata nel CSV:", csv_col))
    }
  }

  nomi_esatti_per_python <- csv_column_names

  print("🚀 Esecuzione predizione clinica...")
  predizione <- "Sconosciuto"

  tryCatch(
    {
      if (inherits(modello, "xgb.Booster")) {
        mat <- as.matrix(dati_nuovo)
        pred_prob <- predict(modello, mat)
        predizione <- ifelse(pred_prob > 0.5, "Malato", "Sano")
      } else {
        pred_raw <- predict(modello, newdata = dati_nuovo, type = "class")
        predizione <- as.character(pred_raw)
      }
    },
    error = function(e) {
      print("⚠️ Fallita pred. classificazione. Tento predizione standard.")
      pred_raw <- predict(modello, newdata = dati_nuovo)
      if (is.list(pred_raw) && !is.null(pred_raw$data$response)) {
        predizione <<- as.character(pred_raw$data$response)
      } else {
        predizione <<- as.character(pred_raw)
      }
    }
  )
  print(paste("🎯 Diagnosi calcolata:", predizione))

  print("🌀 Calcolo UMAP 3D (Fase di Fit e Transform)...")
  plot_data_list <- NULL

  if (!is.null(storico_x) && nrow(storico_x) > 5) {
    set.seed(42)
    n_neigh <- min(15, nrow(storico_x) - 1)

    umap_mappa <- uwot::umap(
      storico_x,
      n_components = 3,
      n_neighbors = n_neigh,
      min_dist = 0.01,
      n_threads = 1,
      ret_model = TRUE
    )
    n_storico <- nrow(storico_x)

    storico_coords_base <- data.frame(
      x = umap_mappa$embedding[, 1],
      y = umap_mappa$embedding[, 2],
      z = umap_mappa$embedding[, 3],
      label = as.character(storico_y),
      stringsAsFactors = FALSE
    )

    storico_df <- as.data.frame(storico_x)

    if (ncol(storico_df) == length(feature_req)) {
      colnames(storico_df) <- nomi_esatti_per_python
    }

    if (".outcome" %in% colnames(storico_df)) {
      storico_df$.outcome <- NULL
    }

    storico_coords <- cbind(storico_coords_base, storico_df)

    id_reali <- rownames(storico_x)
    if (is.null(id_reali) || all(id_reali == as.character(1:n_storico))) {
      storico_coords$subject_id <- paste0("Paziente_Storico_", 1:n_storico)
    } else {
      storico_coords$subject_id <- id_reali
    }

    nuovo_paz_emb <- uwot::umap_transform(
      dati_nuovo,
      umap_mappa,
      n_threads = 1
    )

    dati_nuovo_json <- dati_nuovo
    colnames(dati_nuovo_json) <- nomi_esatti_per_python

    nuovo_paz_coords <- c(
      list(
        x = nuovo_paz_emb[1, 1],
        y = nuovo_paz_emb[1, 2],
        z = nuovo_paz_emb[1, 3]
      ),
      as.list(dati_nuovo_json)
    )

    plot_data_list <- list(
      storico = storico_coords,
      nuovo_paziente = nuovo_paz_coords
    )
  } else {
    print("⚠️ Storico insufficiente o mancante. Salto UMAP.")
  }

  list(
    status = "success",
    task_id = task_id,
    diagnosi_predetta = predizione,
    plot_data = plot_data_list
  )
}
