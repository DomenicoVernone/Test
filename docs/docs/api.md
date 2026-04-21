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

<div class="endpoint-box">

<p>
Clinical Twin espone una serie di endpoint REST distribuiti su microservizi
FastAPI e Plumber (R) che gestiscono autenticazione utenti, orchestrazione
della pipeline radiomica, inferenza diagnostica e interazione con
l’assistente AI context-aware.
</p>

<p>
Queste API consentono l’integrazione della piattaforma con dashboard cliniche,
strumenti di ricerca neuroimaging e workflow automatizzati di analisi MRI.
</p>

</div>


<h2>api_gateway</h2>

<div class="endpoint-box">

<p>
Il servizio <b>api_gateway</b> gestisce autenticazione utenti, autorizzazione
tramite JWT e routing sicuro delle richieste verso i microservizi interni.
</p>

<h3>POST /signup</h3>

<p>
Registra un nuovo utente nella piattaforma Clinical Twin.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>POST /login</h3>

<p>
Autentica l’utente e restituisce un token JWT necessario per accedere
agli endpoint protetti.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>GET /me</h3>

<p>
Restituisce le informazioni dell’utente autenticato associate al token JWT.
</p>

</div>


<h2>orchestrator</h2>

<div class="endpoint-box">

<p>
Il microservizio <b>orchestrator</b> coordina l’esecuzione asincrona della
pipeline neuroimaging tramite Nextflow e monitora lo stato delle analisi MRI.
</p>

<h3>POST /analyze</h3>

<p>
Avvia una nuova pipeline radiomica su una risonanza magnetica precedentemente
caricata nel volume condiviso.
</p>

<div class="codeblock">
{
  "filename": "subject01.nii.gz"
}
</div>

<h3>GET /task/{task_id}</h3>

<p>
Restituisce lo stato corrente dell’elaborazione (queued, running, completed, failed).
</p>

<h3>GET /tasks</h3>

<p>
Restituisce l’elenco completo delle analisi eseguite dall’utente autenticato.
</p>

</div>


<h2>model_service</h2>

<div class="endpoint-box">

<p>
Il servizio <b>model_service</b> gestisce il caricamento dei modelli diagnostici
dal Model Registry MLflow e l’esecuzione della predizione sulle feature radiomiche.
</p>

<h3>POST /load-model</h3>

<p>
Scarica e inizializza il champion model registrato su MLflow/DagsHub.
</p>

<h3>POST /predict</h3>

<p>
Riceve in input feature radiomiche preprocessate e restituisce la predizione diagnostica.
</p>

</div>


<h2>inference_engine</h2>

<div class="endpoint-box">

<p>
Il microservizio <b>inference_engine</b>, implementato in R tramite Plumber,
esegue classificazione KNN e proiezione nello spazio latente UMAP.
</p>

<h3>POST /knn</h3>

<p>
Restituisce la classificazione diagnostica basata su similarità con il dataset
clinico di riferimento.
</p>

<div class="codeblock">
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</div>

<h3>POST /umap</h3>

<p>
Calcola le coordinate tridimensionali del paziente nello spazio latente UMAP
utilizzato per la visualizzazione dei cluster diagnostici.
</p>

</div>


<h2>llm_service</h2>

<div class="endpoint-box">

<p>
Il servizio <b>llm_service</b> fornisce funzionalità di explainability tramite
assistente AI context-aware basato su Spatial-RAG.
</p>

<h3>POST /chat</h3>

<p>
Invia una richiesta testuale all’assistente AI per ottenere interpretazioni
cliniche delle feature radiomiche e della posizione nello spazio diagnostico.
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
La documentazione interattiva completa delle API è disponibile tramite Swagger UI
per ciascun microservizio FastAPI attivo nello stack Docker.
</p>

<div class="codeblock">
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
</div>

<p>
Swagger consente di testare direttamente gli endpoint e verificare le strutture
JSON di request/response durante lo sviluppo o il debugging della pipeline.
</p>

</div>



</div>

</body>
</html>