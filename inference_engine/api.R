# File: inference_engine/api.R # nolint

library(plumber)
library(uwot)
library(jsonlite)
library(caret)
library(xgboost)

VOLUME_DIR <- "/shared_data" # nolint # nolint

#* @apiTitle Clinical Twin - Inference Engine
#* @filter logger
function(req) {
  print(paste("[LOG]", req$REQUEST_METHOD, req$PATH_INFO))
  plumber::forward()
}

#* Calcola Inferenza e UMAP 3D
#* @param task_id L'ID del task
#* @param model_name Il nome del modello
#* @param model_dir La cartella nel volume
#* @post /infer
function(res, task_id, model_name, model_dir) {
  csv_file <- file.path(VOLUME_DIR, paste0("features_", task_id, ".csv"))

  tryCatch(
    {
      print(paste("🔍 Cerco il file .rds scaricato in:", model_dir))
      rds_files <- list.files(model_dir, pattern = "\\.rds$", full.names = TRUE, recursive = TRUE) # nolint: line_length_linter.

      if (length(rds_files) == 0) stop("Nessun file .rds trovato nella cartella scaricata.") # nolint

      rds_file <- rds_files[1]
      print(paste("✅ Trovato artefatto R:", rds_file))

      modello <- readRDS(rds_file)
      # check.names = FALSE impedisce a R di alterare i nomi delle feature (es. togliere spazi o trattini) # nolint
      dati_paziente <- read.csv(csv_file, check.names = FALSE)

      # --- 1. ESTRAZIONE DATI STORICI UNIVERSALE ---
      print("⚙️ Estrazione dati storici dal modello...")
      storico_X <- NULL # nolint
      storico_y <- NULL

      # Supporto Multi-Libreria (mlr, caret puro, etc.)
      if (!is.null(modello$learn$X)) {
        storico_X <- modello$learn$X # nolint
        storico_y <- modello$learn$y
      } else if (!is.null(modello$x)) {
        storico_X <- as.data.frame(modello$x) # nolint: object_name_linter.
        storico_y <- modello$y
      } else if (!is.null(modello$trainingData)) {
        storico_X <- modello$trainingData # nolint: object_name_linter.
        storico_X$.outcome <- NULL # nolint
        storico_y <- modello$trainingData$.outcome
      } else {
        stop("Impossibile estrarre la matrice di training dal modello fornito.")
      }

      # --- 2. DATA ALIGNMENT BLINDATO (Antiproiettile) ---
      print("🛡️ Allineamento dimensionale sicuro...")
      feature_necessarie <- colnames(storico_X)

      # Costruiamo un dataframe vuoto (tutto a 0) con la struttura ESATTA richiesta dal modello # nolint
      dati_nuovo_paz <- data.frame(matrix(0, nrow = 1, ncol = length(feature_necessarie))) # nolint: line_length_linter.
      colnames(dati_nuovo_paz) <- feature_necessarie

      # Copiamo solo i dati che combaciano perfettamente, ignorando tutto il resto senza crashare # nolint: line_length_linter.
      colonne_in_comune <- intersect(feature_necessarie, colnames(dati_paziente)) # nolint: line_length_linter.
      for (col in colonne_in_comune) {
        dati_nuovo_paz[1, col] <- as.numeric(dati_paziente[1, col])
      }

      if (length(colonne_in_comune) < length(feature_necessarie)) {
        print(paste("⚠️ Attenzione: Il CSV forniva solo", length(colonne_in_comune), "feature su", length(feature_necessarie), "richieste. Autocompletamento di sicurezza effettuato.")) # nolint: line_length_linter.
      } else {
        print("✅ Allineamento feature 100% perfetto.")
      }

      # --- 3. UMAP 3D ---
      print("🌀 Calcolo UMAP 3D in corso...")
      dataset_combinato <- rbind(storico_X, dati_nuovo_paz)
      set.seed(42)
      umap_res <- uwot::umap(dataset_combinato, n_components = 3, n_neighbors = 15, min_dist = 0.1) # nolint: line_length_linter.

      # --- 4. PREDIZIONE CLINICA ---
      print("🚀 Esecuzione predizione clinica...")
      predizione <- "Sconosciuto"

      # Blocco tryCatch robusto per supportare le stranezze di mlr, caret e xgboost # nolint: line_length_linter. # nolint: line_length_linter.
      tryCatch(
        {
          if (inherits(modello, "xgb.Booster")) {
            mat <- as.matrix(dati_nuovo_paz)
            pred_prob <- predict(modello, mat)
            predizione <- ifelse(pred_prob > 0.5, "Malato", "Sano")
          } else if (inherits(modello, "knn3")) {
            pred_raw <- predict(modello, newdata = dati_nuovo_paz, type = "class") # nolint: line_length_linter.
            predizione <- as.character(pred_raw)
          } else {
            pred_raw <- predict(modello, newdata = dati_nuovo_paz, type = "class") # nolint: line_length_linter. # nolint: line_length_linter.
            predizione <- as.character(pred_raw)
          }
        },
        error = function(e) {
          print(paste("⚠️ Fallita predizione con type='class'. Tento predizione standard. Dettaglio:", e$message)) # nolint: line_length_linter.
          pred_raw <- predict(modello, newdata = dati_nuovo_paz)

          # Se è un oggetto complesso di tipo mlr Prediction lo spacchetta
          if (is.list(pred_raw) && !is.null(pred_raw$data$response)) {
            predizione <<- as.character(pred_raw$data$response)
          } else {
            predizione <<- as.character(pred_raw)
          }
        }
      )

      print(paste("🎯 Diagnosi calcolata:", predizione))

      # --- 5. COMPOSIZIONE JSON FINALE ---
      n_storico <- nrow(storico_X)
      storico_coords <- data.frame(
        x = umap_res[1:n_storico, 1], y = umap_res[1:n_storico, 2], z = umap_res[1:n_storico, 3], # nolint: line_length_linter.
        label = as.character(storico_y)
      )
      nuovo_paziente_coords <- list(
        x = umap_res[n_storico + 1, 1], y = umap_res[n_storico + 1, 2], z = umap_res[n_storico + 1, 3] # nolint: line_length_linter.
      )

      return(list(
        status = "success", task_id = task_id, diagnosi_predetta = predizione,
        plot_data = list(storico = storico_coords, nuovo_paziente = nuovo_paziente_coords) # nolint: line_length_linter.
      ))
    },
    error = function(e) {
      res$status <- 500
      print(paste("❌ ERRORE CRITICO:", e$message))
      return(list(status = "error", message = e$message)) # nolint: return_linter, line_length_linter.
    }
  )
}
