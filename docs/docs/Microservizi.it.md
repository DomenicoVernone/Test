<!DOCTYPE html>
<html lang="it">

<head>
<meta charset="UTF-8">
<title>Clinical Twin – Microservices Overview</title>

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

/* ===== SERVICE BLOCK ===== */

.service-box {
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
}

</style>
</head>

<body>

<div class="content">

<div class="breadcrumb">
Docs » Microservices Overview
</div>

<h1>Microservices Overview</h1>


<p>
Clinical Twin adotta un’architettura a microservizi containerizzati orchestrati tramite Docker Compose. Ogni servizio implementa una componente funzionale indipendente e comunica con gli altri tramite API REST interne.
</p>


<h2>Panoramica dello stack</h2>

<p>
Il diagramma seguente rappresenta la sequenza logica dei servizi coinvolti durante l’elaborazione di una MRI, dalla gestione dell’utente fino alla visualizzazione dei risultati diagnostici.
</p>

<div class="codeblock">
api_gateway → orchestrator → nextflow_worker → model_service → inference_engine → frontend
                                     ↓
                               llm_service
</div>


<div class="service-box">

<h2>api_gateway</h2>

<p>
Il servizio api_gateway gestisce autenticazione utenti, autorizzazione tramite JWT e accesso sicuro agli endpoint della piattaforma. Costituisce il punto di ingresso principale per tutte le richieste client.
</p>

<ul>
<li>registrazione utenti</li>
<li>login autenticato</li>
<li>generazione e validazione token JWT</li>
<li>routing verso microservizi backend</li>
</ul>

</div>


<div class="service-box">

<h2>orchestrator</h2>

<p>
Il microservizio orchestrator coordina l’esecuzione asincrona delle analisi MRI, gestendo la creazione dei task e l’invocazione della pipeline Nextflow nel servizio nextflow_worker.
</p>

<ul>
<li>creazione task di analisi MRI</li>
<li>monitoraggio stato pipeline</li>
<li>gestione workflow asincroni</li>
<li>propagazione errori tra servizi</li>
</ul>

</div>


<div class="service-box">

<h2>nextflow_worker</h2>

<p>
Il servizio nextflow_worker esegue la pipeline MRI strutturale utilizzando Nextflow e container dedicati per segmentazione anatomica ed estrazione delle feature radiomiche.
</p>

<ul>
<li>preprocessing volumetrico MRI</li>
<li>segmentazione FreeSurfer o FastSurfer</li>
<li>estrazione regioni cerebrali (ROI)</li>
<li>calcolo feature radiomiche PyRadiomics</li>
</ul>

</div>


<div class="service-box">

<h2>model_service</h2>

<p>
Il servizio model_service gestisce l’accesso al Model Registry MLflow su DagsHub e prepara il modello diagnostico utilizzato durante l’inferenza.
</p>

<ul>
<li>download champion model</li>
<li>versioning modelli</li>
<li>integrazione con MLflow</li>
<li>preparazione input per inferenza</li>
</ul>

</div>


<div class="service-box">

<h2>inference_engine</h2>

<p>
Implementato in R tramite Plumber, il servizio inference_engine esegue la classificazione KNN sulle feature radiomiche e calcola la posizione del paziente nello spazio latente UMAP tridimensionale.
</p>

<ul>
<li>stima classe diagnostica</li>
<li>calcolo similarità clinica</li>
<li>embedding UMAP 3D</li>
<li>identificazione nearest neighbors</li>
</ul>

</div>


<div class="service-box">

<h2>llm_service</h2>

<p>
Il servizio llm_service fornisce interpretazione clinica assistita tramite approccio Spatial-RAG, integrando feature radiomiche, coordinate UMAP e contesto conversazionale.
</p>

<ul>
<li>interpretazione feature radiomiche</li>
<li>analisi cluster diagnostici UMAP</li>
<li>supporto explainability del modello</li>
<li>integrazione Groq API</li>
</ul>

</div>


<div class="service-box">

<h2>frontend</h2>

<p>
La dashboard React rappresenta l’interfaccia clinica della piattaforma e consente la gestione delle analisi MRI e l’esplorazione interattiva dei risultati diagnostici.
</p>

<ul>
<li>upload MRI</li>
<li>viewer multiplanare NiiVue</li>
<li>visualizzazione spazio latente UMAP</li>
<li>storico analisi</li>
<li>assistente AI integrato</li>
</ul>

</div>

</div>

</body>

</html>