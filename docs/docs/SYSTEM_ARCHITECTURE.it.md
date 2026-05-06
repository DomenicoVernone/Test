<!DOCTYPE html>

<html lang="it">

<head>
<meta charset="UTF-8">
<title>MLOps – System Architecture</title>

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

<h1>System Architecture</h1>

<div class="section">
<h2>1. Visione generale</h2>

<p>
La piattaforma MLOps è progettata come un sistema distribuito basato su
microservizi containerizzati orchestrati tramite Docker Compose.
L’architettura separa chiaramente le responsabilità tra preprocessing
dei dati, orchestrazione dei workflow, inferenza statistica e
visualizzazione clinica.
</p>

<p>
Questo approccio architetturale consente:
</p>

<ul>
<li>scalabilità indipendente dei componenti</li>
<li>isolamento delle dipendenze software</li>
<li>fault isolation tra microservizi</li>
<li>riproducibilità delle pipeline radiomiche</li>
<li>facilità di estensione e manutenzione</li>
</ul>

</div>

<div class="section">
<h2>2. Architettura distribuita</h2>

<p>
Il sistema è composto da servizi indipendenti containerizzati che
collaborano attraverso API REST e volumi condivisi Docker.
Ogni microservizio implementa una responsabilità specifica
all’interno del workflow MLOps.
</p>

<pre>
Frontend
  ↓
API Gateway
  ↓
Orchestrator
  ↓
Nextflow Worker
  ↓
Inference Engine
  ↓
LLM Service
  ↓
Frontend
</pre>

<p>
La separazione dei componenti permette di aggiornare, distribuire
e scalare i servizi in maniera indipendente senza impattare
l’intera piattaforma.
</p>

</div>

<div class="section">
<h2>3. Flusso dati end-to-end</h2>

<p>
La piattaforma implementa un workflow sequenziale per l’analisi
radiomica delle immagini MRI.
</p>

<pre>
MRI Upload
   ↓
Autenticazione JWT
   ↓
Creazione Task
   ↓
Pipeline Nextflow
   ↓
Estrazione Feature Radiomiche
   ↓
Inferenza Diagnostica
   ↓
Embedding UMAP
   ↓
Explainability AI
   ↓
Visualizzazione Clinica
</pre>

<p>
Ogni fase produce output strutturati che vengono utilizzati
dal servizio successivo, garantendo modularità e tracciabilità
dell’intero workflow.
</p>

</div>

<div class="section">
<h2>4. Struttura dei microservizi</h2>

<table>

<tr>
<th>Servizio</th>
<th>Responsabilità architetturale</th>
<th>Tecnologia</th>
</tr>

<tr>
<td>api_gateway</td>
<td>Security layer e routing centralizzato</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Workflow coordination e task management</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Pipeline radiomica distribuita</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Inferenza ML e spazio latente UMAP</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>model_service</td>
<td>Model Registry e versioning</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>llm_service</td>
<td>Explainability AI e interpretazione clinica</td>
<td>FastAPI, LLM API</td>
</tr>

<tr>
<td>frontend</td>
<td>Interfaccia clinica e visualizzazione</td>
<td>React</td>
</tr>

</table>

</div>

<div class="section">
<h2>5. Comunicazione tra servizi</h2>

<p>
La piattaforma adotta un approccio di comunicazione ibrido:
</p>

<ul>
<li>API REST (HTTP/JSON) per orchestrazione e controllo</li>
<li>volumi Docker condivisi per file MRI e output pipeline</li>
</ul>

<p>
Questo modello riduce l’overhead di trasferimento dei file voluminosi
e migliora l’interoperabilità tra componenti sviluppati con
tecnologie differenti.
</p>

</div>

<div class="section">
<h2>6. Gestione dello stato</h2>

<p>
L’orchestrator mantiene il ciclo di vita dei task tramite
uno stato centralizzato.
</p>

<pre>
pending → running → completed / failed
</pre>

<p>
Questo approccio consente monitoraggio, fault recovery
e gestione asincrona delle pipeline MRI.
</p>

</div>

<div class="section">
<h2>7. Principi architetturali</h2>

<ul>
<li>microservizi → modularità e isolamento</li>
<li>Docker → portabilità e consistenza ambientale</li>
<li>Nextflow → riproducibilità scientifica</li>
<li>MLflow → tracciabilità dei modelli</li>
<li>REST APIs → interoperabilità tra servizi</li>
<li>separazione model/inference → flessibilità architetturale</li>
</ul>

</div>

<div class="section">
<h2>8. Scalabilità e deployment</h2>

<p>
L’architettura è progettata per supportare sia ambienti di ricerca
che deployment production-grade.
</p>

<ul>
<li>scaling indipendente dei microservizi</li>
<li>parallelizzazione delle pipeline Nextflow</li>
<li>supporto per ambienti HPC</li>
<li>containerizzazione completa dei componenti</li>
<li>deployment distribuito tramite Docker Compose</li>
</ul>

</div>

<div class="section">
<h2>9. Benefici architetturali</h2>

<ul>
<li>alta modularità del sistema</li>
<li>maggiore manutenibilità</li>
<li>facilità di testing dei servizi</li>
<li>riduzione dell’accoppiamento tra componenti</li>
<li>riproducibilità delle analisi cliniche</li>
<li>facilità di integrazione di nuovi modelli AI</li>
</ul>

</div>

</div>

</body>

</html>