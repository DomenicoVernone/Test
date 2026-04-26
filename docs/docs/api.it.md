<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – API Reference</title>

<style>

/* ===== GLOBAL ===== */

body {
    margin: 0;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    background: #f5f6f7;
}

/* ===== CONTENT ===== */

.content {
    margin-left: 0px;
    padding: 40px;
    max-width: 900px;
}

/* ===== BREADCRUMB ===== */

.breadcrumb {
    color: #6c6c6c;
    font-size: 14px;
    margin-bottom: 10px;
}

/* ===== HEADINGS ===== */

h1 {
    font-size: 36px;
    margin-bottom: 25px;
}

h2 {
    margin-top: 40px;
    font-size: 26px;
}

h3 {
    margin-top: 15px;
}

/* ===== SERVICE BLOCK ===== */

.endpoint-box {
    background: white;
    padding: 18px;
    border-radius: 8px;
    margin-top: 20px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}

/* ===== CODE BLOCK ===== */

.codeblock {
    background: #eeeeee;
    padding: 14px;
    border-radius: 6px;
    font-family: monospace;
    margin: 15px 0;
    white-space: pre-line;
}

/* ===== FOOTER ===== */

.footer {
    margin-top: 50px;
    font-size: 14px;
    color: gray;
}

</style>
</head>

<body>

<div class="content">

<div class="breadcrumb">
Docs » API Reference
</div>

<h1>API Reference</h1>

<p>
Questa sezione descrive gli endpoint REST esposti dai microservizi Clinical Twin
per autenticazione utenti, orchestrazione pipeline MRI, inferenza diagnostica
e interpretazione AI dei risultati.
</p>

<div class="endpoint-box">

<p>
Le API sono implementate tramite FastAPI (Python) e Plumber (R) e consentono
l’integrazione della piattaforma con dashboard cliniche, workflow automatizzati
e strumenti di ricerca neuroimaging. Gli endpoint protetti richiedono un token JWT.
</p>

</div>


<h2>api_gateway</h2>

<div class="endpoint-box">

<p>
Il servizio <b>api_gateway</b> gestisce autenticazione utenti, generazione JWT
e accesso sicuro agli endpoint protetti.
</p>

<h3>POST /signup</h3>

<p>
Registra un nuovo utente.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>POST /login</h3>

<p>
Autentica l’utente e restituisce un token JWT da includere nelle richieste successive.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>GET /me</h3>

<p>
Restituisce le informazioni dell’utente associato al token JWT corrente.
</p>

</div>


<h2>orchestrator</h2>

<div class="endpoint-box">

<p>
Il microservizio <b>orchestrator</b> avvia e monitora l’esecuzione della pipeline
Nextflow su dataset MRI caricati nel volume condiviso.
</p>

<h3>POST /analyze</h3>

<p>
Avvia una nuova analisi su una MRI già disponibile nel volume condiviso Docker.
Richiede autenticazione JWT.
</p>

<div class="codeblock">
{
  "filename": "subject01.nii.gz"
}
</div>

<h3>GET /task/{task_id}</h3>

<p>
Restituisce lo stato dell’elaborazione (queued, running, completed, failed).
</p>

<h3>GET /tasks</h3>

<p>
Restituisce l’elenco delle analisi avviate dall’utente autenticato.
</p>

</div>


<h2>model_service</h2>

<div class="endpoint-box">

<p>
Il servizio <b>model_service</b> recupera i modelli diagnostici dal registry MLflow
e gestisce la preparazione delle predizioni sulle feature radiomiche estratte.
</p>

<h3>POST /load-model</h3>

<p>
Scarica e inizializza il champion model dal Model Registry MLflow/DagsHub.
</p>

<h3>POST /predict</h3>

<p>
Riceve feature radiomiche preprocessate e restituisce la predizione diagnostica
utilizzando il modello attivo.
</p>

</div>


<h2>inference_engine</h2>

<div class="endpoint-box">

<p>
Il microservizio <b>inference_engine</b> (Plumber/R) esegue classificazione KNN
e proiezione UMAP nello spazio latente diagnostico.
</p>

<h3>POST /knn</h3>

<p>
Restituisce la classe diagnostica stimata e il relativo confidence score
basati sulla similarità con il dataset di riferimento.
</p>

<div class="codeblock">
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</div>

<h3>POST /umap</h3>

<p>
Calcola le coordinate tridimensionali del paziente nello spazio UMAP utilizzato
per visualizzazione e analisi dei cluster diagnostici.
</p>

</div>


<h2>llm_service</h2>

<div class="endpoint-box">

<p>
Il servizio <b>llm_service</b> fornisce funzionalità di explainability tramite
assistente AI basato su Spatial-RAG.
</p>

<h3>POST /chat</h3>

<p>
Invia una richiesta testuale all’assistente AI per ottenere interpretazioni
cliniche basate su feature radiomiche, posizione UMAP e contesto diagnostico.
</p>

<div class="codeblock">
{
  "message": "Explain this patient's cluster position"
}
</div>

</div>


<h2>Swagger UI</h2>

<div class="endpoint-box">

<p>
La documentazione interattiva completa è disponibile tramite Swagger UI
per ciascun microservizio FastAPI attivo nello stack.
</p>

<div class="codeblock">
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
</div>

<p>
Swagger consente di testare gli endpoint, verificare le strutture JSON
di request/response e monitorare il comportamento dei servizi durante sviluppo
e debugging.
</p>

</div>


</div>

</body>
</html>