# plumber.R

#* @apiTitle Modello di Inferenza FTD

#* Finta predizione del modello ML
#* @param id_paziente L'ID del paziente da analizzare
#* @get /predict
function(id_paziente="") {
  list(
    patient_id = id_paziente,
    probability_FTD = 0.85,
    status = "Analisi completata"
  )
}