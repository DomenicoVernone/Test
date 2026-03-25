# File: inference_engine/api.R
#
# Router HTTP Plumber per l'inference engine R.
# Responsabilita':
#   - Ricevere le richieste di inferenza dall'orchestrator Python (via model_service)
#   - Delegare il calcolo matematico a R/inference_logic.R
#   - Salvare il risultato JSON nel volume condiviso
#   - Restituire il risultato all'orchestrator

library(plumber)
library(jsonlite)

source("R/inference_logic.R")

volume_dir <- Sys.getenv("SHARED_VOLUME_DIR", unset = "/shared_data")

#* @apiTitle Clinical Twin - Inference Engine
#* @filter logger
function(req) {
  message(paste("[API]", req$REQUEST_METHOD, req$PATH_INFO))
  plumber::forward()
}

#* Esegue inferenza clinica e calcolo UMAP 3D
#* @param task_id ID del task
#* @param model_name Nome del modello
#* @param model_dir Path assoluto del file .rds scaricato da MLflow
#* @post /infer
function(res, task_id, model_name, model_dir) {

  csv_file <- file.path(volume_dir, "features", paste0("features_", task_id, ".csv"))

  tryCatch(
    {
      risultato <- run_clinical_inference(
        task_id  = task_id,
        model_dir = model_dir,
        csv_file  = csv_file
      )

      results_dir <- file.path(volume_dir, "results")
      if (!dir.exists(results_dir)) {
        dir.create(results_dir, recursive = TRUE)
      }

      out_file <- file.path(results_dir, paste0("result_", task_id, ".json"))
      jsonlite::write_json(risultato, out_file, auto_unbox = TRUE)
      message(paste("[API] Risultato salvato:", out_file))

      # Pausa intenzionale: il model_service Python legge il file JSON immediatamente
      # dopo la risposta HTTP. Senza questa attesa, la write_json puo' non essere
      # ancora stata completata dal buffer del filesystem al momento della lettura.
      Sys.sleep(1.5)

      risultato
    },
    error = function(e) {
      res$status <- 500
      message(paste("[API] ERRORE:", e$message))
      list(
        status  = "error",
        message = paste("Errore durante l'inferenza R:", e$message)
      )
    }
  )
}