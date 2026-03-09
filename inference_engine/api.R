# File: inference_engine/api.R # nolint

library(plumber)
library(uwot)
library(jsonlite)
library(caret)
library(xgboost)

VOLUME_DIR <- "/shared_data"

#* @apiTitle Clinical Twin - Inference Engine
#* @filter logger
function(req) {
  print(paste("[LOG]", req$REQUEST_METHOD, req$PATH_INFO))
  plumber::forward()
}

#* Calcola Inferenza e UMAP 3D
#* @param task_id L'ID del task
#* @param model_name Il nome del modello
#* @param model_dir La cartella nel volume (che ora contiene il percorso ESATTO del file .rds)
#* @post /infer
function(res, task_id, model_name, model_dir) {
  csv_file <- file.path(VOLUME_DIR, "features", paste0("features_", task_id, ".csv"))

  tryCatch(
    {
      # --- 1. LOAD MODEL (Ottimizzato per percorso esatto) ---
      model_path <- model_dir
      print(paste("🔍 Caricamento del modello esatto da:", model_path))

      if (!file.exists(model_path)) {
        stop(paste("File del modello non trovato:", model_path))
      }

      modello <- readRDS(model_path)
      dati_paziente <- read.csv(csv_file, check.names = FALSE)
      print("✅ Artefatto R e dati paziente caricati con successo!")

      # --- 2. ESTRAZIONE DATI STORICI (BLINDATA) ---
      print("⚙️ Estrazione dati storici dal modello...")
      storico_X <- NULL
      storico_y <- NULL
      feature_necessarie <- NULL

      if (!is.null(modello$trainingData)) {
        storico_X <- modello$trainingData
        if (".outcome" %in% colnames(storico_X)) {
          storico_y <- storico_X$.outcome
          storico_X$.outcome <- NULL
        }
        feature_necessarie <- colnames(storico_X)
      } else if (!is.null(modello$learn$X)) {
        storico_X <- modello$learn$X
        storico_y <- modello$learn$y
        feature_necessarie <- colnames(storico_X)
      } else if (!is.null(modello$x)) {
        storico_X <- as.data.frame(modello$x)
        storico_y <- modello$y
        feature_necessarie <- colnames(storico_X)
      }

      # Se non abbiamo trovato le feature, proviamo a estrarle dalla struttura del KNN
      if (is.null(feature_necessarie)) {
        if (!is.null(modello$coefnames)) {
          feature_necessarie <- modello$coefnames
        } else if (!is.null(modello$terms)) {
          feature_necessarie <- attr(modello$terms, "term.labels")
        }
      }

      if (is.null(feature_necessarie)) {
        stop("Impossibile dedurre le feature necessarie dal modello (formato sconosciuto).")
      }

      # --- 3. DATA ALIGNMENT ---
      print("🛡️ Allineamento dimensionale sicuro...")
      dati_nuovo_paz <- data.frame(matrix(0, nrow = 1, ncol = length(feature_necessarie)))
      colnames(dati_nuovo_paz) <- feature_necessarie

      colonne_in_comune <- intersect(feature_necessarie, colnames(dati_paziente))

      for (col in colonne_in_comune) {
        dati_nuovo_paz[1, col] <- as.numeric(dati_paziente[1, col])
      }

      # --- 4. PREDIZIONE CLINICA ---
      print("🚀 Esecuzione predizione clinica...")
      predizione <- "Sconosciuto"

      tryCatch(
        {
          if (inherits(modello, "xgb.Booster")) {
            mat <- as.matrix(dati_nuovo_paz)
            pred_prob <- predict(modello, mat)
            predizione <- ifelse(pred_prob > 0.5, "Malato", "Sano")
          } else {
            pred_raw <- predict(modello, newdata = dati_nuovo_paz, type = "class")
            predizione <- as.character(pred_raw)
          }
        },
        error = function(e) {
          print("⚠️ Fallita predizione class. Tento predizione standard.")
          pred_raw <- predict(modello, newdata = dati_nuovo_paz)
          if (is.list(pred_raw) && !is.null(pred_raw$data$response)) {
            predizione <<- as.character(pred_raw$data$response)
          } else {
            predizione <<- as.character(pred_raw)
          }
        }
      )
      print(paste("🎯 Diagnosi calcolata:", predizione))

      # --- 5. UMAP 3D (Spazio Congelato / Proiezione Clinica) ---
      print("🌀 Calcolo UMAP 3D (Fase di Fit e Transform)...")
      plot_data_list <- NULL

      if (!is.null(storico_X) && nrow(storico_X) > 5) {
        set.seed(42)

        # Il vicinato si calcola SOLO sui pazienti storici
        n_neigh <- min(15, nrow(storico_X) - 1)

        # 1. FIT (Congelamento): Creiamo lo spazio topologico SOLO sullo storico
        # ret_model = TRUE ci salva la "mappa" per usarla dopo
        umap_mappa <- uwot::umap(storico_X, n_components = 3, n_neighbors = n_neigh, min_dist = 0.1, n_threads = 1, ret_model = TRUE)

        n_storico <- nrow(storico_X)
        storico_coords <- data.frame(
          x = umap_mappa$embedding[, 1],
          y = umap_mappa$embedding[, 2],
          z = umap_mappa$embedding[, 3],
          label = as.character(storico_y)
        )

        # Manteniamo gli ID originali per pulizia
        id_reali <- rownames(storico_X)
        if (is.null(id_reali) || all(id_reali == as.character(1:n_storico))) {
          storico_coords$subject_id <- paste0("Paziente_Storico_", 1:n_storico)
        } else {
          storico_coords$subject_id <- id_reali
        }

        # 2. TRANSFORM (Proiezione): "Caliamo" il nuovo paziente nello spazio congelato
        # Le coordinate dello storico resteranno matematicamente intatte e immobili
        nuovo_paziente_embedding <- uwot::umap_transform(dati_nuovo_paz, umap_mappa, n_threads = 1)

        nuovo_paziente_coords <- list(
          x = nuovo_paziente_embedding[1, 1],
          y = nuovo_paziente_embedding[1, 2],
          z = nuovo_paziente_embedding[1, 3]
        )

        plot_data_list <- list(storico = storico_coords, nuovo_paziente = nuovo_paziente_coords)
      } else {
        print("⚠️ Storico insufficiente o mancante. Salto UMAP.")
      }

      # --- 6. COMPOSIZIONE JSON FINALE (Solo Dati Reali) ---
      return(list(
        status = "success",
        task_id = task_id,
        diagnosi_predetta = predizione,
        plot_data = plot_data_list
      ))
    },
    error = function(e) {
      res$status <- 500
      print(paste("❌ ERRORE CRITICO:", e$message))
      return(list(status = "error", message = e$message))
    }
  )
}
