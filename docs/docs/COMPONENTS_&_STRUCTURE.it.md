<!DOCTYPE html>

<html lang="it">

<head>
<meta charset="UTF-8">
<title>MLOps – Componenti del Sistema e Struttura del Progetto</title>

<style>
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 40px;
    background-color: #f9f9f9;
    color: #333;
}

h1, h2, h3 {
    color: #2c3e50;
}

h1 {
    border-bottom: 2px solid #ccc;
    padding-bottom: 10px;
}

pre {
    background-color: #eee;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

.section {
    margin-bottom: 40px;
}

.box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

ul {
    margin-left: 20px;
}

/* ===== TABLE STYLE UNIFICATO ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
    font-size: 14px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
}

th {
    background-color: #2c3e50;
    color: white;
    text-align: left;
    padding: 12px;
    font-weight: 600;
}

td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

tr:hover {
    background-color: #eef2f5;
}
</style>

</head>

<body>

<div class="box">

<h1>Componenti del Sistema e Struttura del Progetto</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
La piattaforma MLOps è organizzata come un sistema distribuito composto
da microservizi indipendenti, ciascuno responsabile di una specifica
fase del workflow radiomico.
</p>

<p>
La struttura del progetto riflette questa architettura, consentendo:
</p>

<ul>
<li>modularità dei componenti</li>
<li>separazione delle responsabilità</li>
<li>manutenibilità del codice</li>
<li>scalabilità indipendente dei servizi</li>
<li>facilità di estensione della piattaforma</li>
</ul>

</div>

<div class="section">
<h2>2. Struttura del repository</h2>

<p>
Il repository è organizzato in directory separate, ciascuna associata
a un microservizio o a un componente principale della piattaforma.
</p>

<pre>
Tesi-FTD/
├── api_gateway/
├── orchestrator/
├── model_service/
├── llm_service/
├── inference_engine/
├── nextflow_worker/
└── frontend/
</pre>

<p>
Ogni directory contiene il codice sorgente, i file di configurazione
e le definizioni Docker necessarie per l’esecuzione del servizio
corrispondente.
</p>

</div>

<div class="section">
<h2>3. Panoramica dei microservizi</h2>

<table>

<tr>
<th>Servizio</th>
<th>Ruolo</th>
<th>Tecnologia</th>
</tr>

<tr>
<td>api_gateway</td>
<td>Autenticazione, autorizzazione e routing delle richieste</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Gestione workflow e coordinamento pipeline</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Esecuzione pipeline MRI e radiomica</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Inferenza diagnostica e embedding UMAP</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>model_service</td>
<td>Gestione modelli e versioning</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>llm_service</td>
<td>Explainability AI e interpretazione clinica</td>
<td>FastAPI, LLM API</td>
</tr>

<tr>
<td>frontend</td>
<td>Interfaccia utente e visualizzazione clinica</td>
<td>React</td>
</tr>

</table>

</div>

<div class="section">
<h2>4. Descrizione dei servizi</h2>

<h3>api_gateway</h3>
<p>
Rappresenta il punto di ingresso della piattaforma.
Gestisce l’autenticazione tramite JWT e instrada le richieste
verso i servizi interni.
</p>

<h3>orchestrator</h3>
<p>
Coordina l’esecuzione delle analisi MRI e gestisce il workflow
della pipeline radiomica. Mantiene lo stato dei task e supervisiona
la comunicazione tra i servizi.
</p>

<h3>nextflow_worker</h3>
<p>
Esegue la pipeline di neuroimaging tramite Nextflow.
Processa i dati MRI, esegue segmentazione, estrae feature
radiomiche e genera output strutturati.
</p>

<h3>inference_engine</h3>
<p>
Esegue l’inferenza diagnostica utilizzando modelli di machine learning.
Applica classificazione KNN e proiezione nello spazio latente tramite UMAP.
</p>

<h3>model_service</h3>
<p>
Gestisce il ciclo di vita dei modelli tramite MLflow,
inclusi recupero, versioning e integrazione con registry esterni
come DagsHub.
</p>

<h3>llm_service</h3>
<p>
Fornisce explainability tramite modelli AI, generando interpretazioni
cliniche contestualizzate basate sulle feature radiomiche
e sui risultati di inferenza.
</p>

<h3>frontend</h3>
<p>
Implementa l’interfaccia utente in React, permettendo l’upload
delle MRI, il monitoraggio della pipeline e la visualizzazione
dei risultati diagnostici.
</p>

</div>

<div class="section">
<h2>5. Comunicazione tra servizi</h2>

<p>
I microservizi comunicano tramite un approccio ibrido:
</p>

<ul>
<li>API REST (HTTP/JSON) per controllo e orchestrazione</li>
<li>volumi Docker condivisi per dati MRI e output della pipeline</li>
</ul>

<p>
Questa architettura consente di gestire efficientemente file
voluminosi e garantisce interoperabilità tra servizi eterogenei.
</p>

</div>

<div class="section">
<h2>6. Flusso operativo</h2>

<pre>
Frontend
   ↓
API Gateway
   ↓
Orchestrator
   ↓
Nextflow Worker
   ↓
Radiomics Features (CSV)
   ↓
Inference Engine
   ↓
LLM Service
   ↓
Frontend
</pre>

<p>
Ogni componente opera in modo indipendente contribuendo a una
pipeline di analisi coerente, modulare e riproducibile.
</p>

</div>

<div class="section">
<h2>7. Scelte progettuali</h2>

<ul>
<li>microservizi → modularità e scalabilità indipendente</li>
<li>Docker → isolamento e riproducibilità</li>
<li>Nextflow → workflow scientifici deterministici</li>
<li>separazione delle responsabilità → maggiore manutenibilità</li>
<li>servizi indipendenti → fault isolation</li>
</ul>

<p>
Queste scelte progettuali garantiscono che il sistema sia
estensibile, robusto e adatto sia a contesti di ricerca
che a scenari di produzione.
</p>

</div>

</div>

</body>

</html>