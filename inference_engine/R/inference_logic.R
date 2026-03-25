# File: inference_engine/R/inference_logic.R
#
# Logica di inferenza clinica e calcolo topologico UMAP 3D.
# Questo modulo non ha dipendenze dal layer web (Plumber): contiene
# esclusivamente matematica e I/O su filesystem.
#
# Flusso principale (run_clinical_inference):
#   1. Carica il modello .rds e il CSV delle feature del paziente
#   2. Estrae i dati di training storici dal modello per costruire lo spazio UMAP
#   3. Allinea le colonne CSV alle feature attese dal modello tramite mapping ROI
#   4. Esegue la predizione (classificazione)
#   5. Calcola l'embedding UMAP 3D e proietta il nuovo paziente nello spazio storico
#   6. Restituisce un oggetto lista serializzabile in JSON

library(uwot)
library(caret)
library(xgboost)


#' Esegue la pipeline di inferenza e calcola l'embedding UMAP 3D
#' @param task_id ID del task corrente
#' @param model_dir Percorso esatto del file .rds scaricato da MLflow
#' @param csv_file Percorso esatto del file CSV contenente le feature del paziente
run_clinical_inference <- function(task_id, model_dir, csv_file) {
  message(paste("[INFERENCE] Caricamento modello:", model_dir))
  if (!file.exists(model_dir)) {
    stop(paste("File del modello non trovato:", model_dir))
  }

  modello <- readRDS(model_dir)
  dati_paziente <- read.csv(csv_file, check.names = FALSE)
  message("[INFERENCE] Modello e dati paziente caricati.")

  # Estrazione dati storici dal modello.
  # Il formato dipende dal tipo di modello (caret, ranger, xgboost):
  # si tenta in ordine trainingData, learn$X, x.
  message("[INFERENCE] Estrazione dati storici dal modello...")
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

  # Mapping deterministico tra feature del modello e colonne del CSV.
  #
  # Il CSV e' generato da merge_radiomics.r, che itera le 78 ROI in ordine.
  # La prima ROI genera colonne senza suffisso numerico; la seconda aggiunge ".1",
  # la terza ".2", e cosi' via. Il suffisso N corrisponde alla ROI all'indice N+1
  # nel file labels. Questo mapping ricostruisce il nome CSV corretto per ogni
  # feature attesa dal modello.
  message("[INFERENCE] Allineamento feature tramite mapping ROI...")

  roi_labels_path <- Sys.getenv("NF_LABELS")
  if (nchar(roi_labels_path) == 0) {
    stop("Variabile NF_LABELS non definita. Il file ROI labels deve essere fornito dalla pipeline Nextflow.")
  }  
  roi_labels <- read.table(roi_labels_path, header = FALSE, sep = "")
  roi_names <- roi_labels$V3 # 78 ROI in ordine

  build_roi_mapping <- function(feature_req, roi_names) {
    mapping <- character(length(feature_req))
    for (i in seq_along(feature_req)) {
      fname <- feature_req[i]
      suffix_match <- regmatches(fname, regexpr("\\.[0-9]+$", fname))
      if (length(suffix_match) == 0 || suffix_match == "") {
        roi_idx <- 1
        base_name <- fname
      } else {
        roi_idx <- as.integer(sub("\\.", "", suffix_match)) + 1
        base_name <- sub("\\.[0-9]+$", "", fname)
      }
      if (roi_idx > length(roi_names)) {
        message(paste("[INFERENCE] Indice ROI fuori range:", roi_idx, "per feature:", fname))
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
      message(paste("[INFERENCE] Colonna non trovata nel CSV:", csv_col))
    }
  }

  nomi_esatti_per_python <- csv_column_names

  # Predizione: il comportamento dipende dal tipo di modello.
  # XGBoost restituisce probabilita' continue; gli altri modelli caret
  # supportano type="class". Il fallback intercetta modelli non standard.
  message("[INFERENCE] Esecuzione predizione clinica...")
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
      message("[INFERENCE] Predizione con type='class' fallita, tento predizione standard.")
      pred_raw <- predict(modello, newdata = dati_nuovo)
      if (is.list(pred_raw) && !is.null(pred_raw$data$response)) {
        predizione <<- as.character(pred_raw$data$response)
      } else {
        predizione <<- as.character(pred_raw)
      }
    }
  )
  message(paste("[INFERENCE] Diagnosi calcolata:", predizione))

  # UMAP 3D: fit sullo storico, transform sul nuovo paziente.
  # ret_model=TRUE e' necessario per poter chiamare umap_transform successivamente.
  # n_threads=1 garantisce riproducibilita' in combinazione con set.seed(42).
  message("[INFERENCE] Calcolo embedding UMAP 3D...")
  plot_data_list <- NULL

  if (!is.null(storico_x) && nrow(storico_x) > 5) {
    set.seed(42)
    n_neigh <- min(15, nrow(storico_x) - 1)

    umap_mappa <- uwot::umap(
      storico_x,
      n_components = 3,
      n_neighbors  = n_neigh,
      min_dist     = 0.01,
      n_threads    = 1,
      ret_model    = TRUE
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
      storico        = storico_coords,
      nuovo_paziente = nuovo_paz_coords
    )
  } else {
    message("[INFERENCE] Storico insufficiente o mancante. UMAP saltato.")
  }

  list(
    status = "success",
    task_id = task_id,
    diagnosi_predetta = predizione,
    plot_data = plot_data_list
  )
}
