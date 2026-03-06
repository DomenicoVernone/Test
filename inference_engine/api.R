# inference_engine/api.R

library(plumber)

# Percorsi nel container Docker (Volume Condiviso)
VOLUME_DIR <- "/shared_data"
MODELS_DIR <- paste0(VOLUME_DIR, "/models")

#* @apiTitle FTD Statistical Inference Engine
#* @apiDescription Microservizio in R per l'esecuzione dei modelli ML di Pracella

#* @filter logger
function(req){
  print(paste("Ricevuta richiesta:", req$REQUEST_METHOD, req$PATH_INFO))
  plumber::forward()
}

#* Esegue la predizione sul file CSV generato dalla pipeline
#* @param task_id:int L'ID del task (per trovare il file CSV)
#* @param model_name:str Il nome del modello da usare (es. HC_vs_bvFTD)
#* @post /predict
function(res, task_id, model_name) {
  
  csv_file <- paste0(VOLUME_DIR, "/features_", task_id, ".csv")
  rds_file <- paste0(MODELS_DIR, "/", model_name, "/model.rds") # MLflow di solito salva come model.rds dentro la cartella
  
  # --- MODALITÀ SIMULAZIONE (In attesa di Donato) ---
  if (!file.exists(rds_file)) {
    print(paste("⚠️ [Plumber] Modello", rds_file, "non trovato. Uso simulazione..."))
    
    # Se il CSV esiste almeno leggiamolo per dimostrare che il volume funziona
    if(file.exists(csv_file)) {
       print(paste("✅ [Plumber] Letto con successo il CSV dal volume condiviso:", csv_file))
    }
    
    # Restituiamo una diagnosi finta
    return(list(
      status = "success",
      diagnosi = "bvFTD (Simulata)",
      probabilita = 0.85,
      messaggio = "In attesa del modello reale da DagsHub"
    ))
  }
  
  # --- MODALITÀ REALE ---
  tryCatch({
    # 1. Carica il modello
    modello <- readRDS(rds_file)
    
    # 2. Carica i dati estratti da Nextflow
    dati_paziente <- read.csv(csv_file)
    
    # 3. Filtering Dinamico (Prende solo le feature richieste dal modello)
    # Assumiamo che il modello abbia l'attributo $xNames come visto nello screenshot
    feature_necessarie <- modello$xNames
    dati_filtrati <- dati_paziente[, feature_necessarie, drop = FALSE]
    
    # 4. Inferenza
    predizione <- predict(modello, dati_filtrati, type = "class")
    
    return(list(
      status = "success",
      diagnosi = as.character(predizione),
      messaggio = "Inferenza completata con successo"
    ))
    
  }, error = function(e) {
    res$status <- 500
    return(list(status = "error", message = paste("Errore in R:", e$message)))
  })
}