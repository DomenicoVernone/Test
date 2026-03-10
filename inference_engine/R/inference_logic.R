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

  print("🛡️ Allineamento dimensionale sicuro...")
  dati_nuovo <- data.frame(
    matrix(0, nrow = 1, ncol = length(feature_req))
  )
  colnames(dati_nuovo) <- feature_req

  col_comuni <- intersect(feature_req, colnames(dati_paziente))
  for (col in col_comuni) {
    dati_nuovo[1, col] <- as.numeric(dati_paziente[1, col])
  }

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
      min_dist = 0.1,
      n_threads = 1,
      ret_model = TRUE
    )
    n_storico <- nrow(storico_x) # <--- QUESTA È LA RIGA CHE AVEVAMO PERSO!
    # Costruisce il dataframe base con le coordinate spaziali
    storico_coords_base <- data.frame(
      x = umap_mappa$embedding[, 1],
      y = umap_mappa$embedding[, 2],
      z = umap_mappa$embedding[, 3],
      label = as.character(storico_y)
    )

    # NOVITÀ: Idratazione dei dati. Uniamo le coordinate spaziali con TUTTE le feature originali.
    # Usiamo cbind (column bind) per attaccare il dataframe storico_x a storico_coords_base.
    storico_coords <- cbind(storico_coords_base, storico_x)

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

    nuovo_paz_coords <- list(
      x = nuovo_paz_emb[1, 1],
      y = nuovo_paz_emb[1, 2],
      z = nuovo_paz_emb[1, 3]
    )

    plot_data_list <- list(
      storico = storico_coords,
      nuovo_paziente = nuovo_paz_coords
    )
  } else {
    print("⚠️ Storico insufficiente o mancante. Salto UMAP.")
  }

  # Return implicito (lintr rule)
  list(
    status = "success",
    task_id = task_id,
    diagnosi_predetta = predizione,
    plot_data = plot_data_list
  )
}
