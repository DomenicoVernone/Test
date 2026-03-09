# File: inference_engine/api.R
#' Router API Plumber
#' Gestisce gli endpoint HTTP e il salvataggio su File System (I/O).

library(plumber)
library(jsonlite)

source("R/inference_logic.R")

volume_dir <- Sys.getenv("SHARED_VOLUME_DIR", unset = "/shared_data")

#* @apiTitle Clinical Twin - Inference Engine Router
#* @filter logger
function(req) {
  print(paste("[LOG API]", req$REQUEST_METHOD, req$PATH_INFO))
  plumber::forward()
}

#* Calcola Inferenza e UMAP 3D
#* @param task_id L'ID del task
#* @param model_name Il nome del modello
#* @param model_dir La cartella nel volume contenente l'artefatto .rds
#* @post /infer
function(res, task_id, model_name, model_dir) {

  file_name <- paste0("features_", task_id, ".csv")
  csv_file <- file.path(volume_dir, "features", file_name)

  tryCatch(
    {
      # 1. Calcolo matematico
      risultato <- run_clinical_inference(
        task_id = task_id,
        model_dir = model_dir,
        csv_file = csv_file
      )
       # nolint: trailing_whitespace_linter.
      # 2. Salvataggio nel Volume
      results_dir <- file.path(volume_dir, "results")
      if (!dir.exists(results_dir)) {
        dir.create(results_dir, recursive = TRUE)
      }
       # nolint: trailing_whitespace_linter, trailing_whitespace_linter, indentation_linter.
      # FIX: Ora il nome combacia esattamente con quello che Python (analyze.py) cerca! # nolint: line_length_linter.
      out_file <- file.path(results_dir, paste0("result_", task_id, ".json"))
       # nolint: trailing_whitespace_linter, indentation_linter.
      jsonlite::write_json(risultato, out_file, auto_unbox = TRUE)
      print(paste("✅ Dati UMAP salvati in:", out_file))
      
      # Pausa per prevenire la Race Condition di Docker
      Sys.sleep(1.5)
      
      risultato
    },
    error = function(e) {
      res$status <- 500
      print(paste("❌ ERRORE CRITICO API:", e$message))

      list(
        status = "error",
        message = paste("Errore durante l'inferenza R:", e$message)
      )
    }
  )
}