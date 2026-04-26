<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – System Architecture</title>

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

/* ===== SERVICE BOX ===== */

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
    white-space: pre-line;
}

/* ===== TABLE ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
}

th {
    background: #f0f0f0;
}

/* ===== IMAGE BLOCK ===== */

.arch-image {
    text-align: center;
}

.arch-image img {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}

.caption {
    font-size: 14px;
    color: gray;
    margin-top: 10px;
}

/* ===== NAV BUTTONS ===== */

.nav-buttons {
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
}

.button {
    background: #e0e0e0;
    border-radius: 6px;
    padding: 10px 15px;
    text-decoration: none;
    color: black;
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
Docs » System Architecture
</div>

<h1>System Architecture</h1>


<div class="service-box">

<p>
Clinical Twin è progettato come una piattaforma modulare basata su
microservizi containerizzati orchestrati tramite Docker Compose.
L’architettura separa chiaramente preprocessing neuroimaging, inferenza
statistica, gestione modelli e interfaccia clinica.
</p>

</div>


<h2>Panoramica generale</h2>

<div class="service-box">

<p>
Il diagramma seguente rappresenta la struttura logica dei microservizi e
il flusso dei dati all’interno della pipeline Clinical Twin.
</p>

<div class="arch-image">
<img src="../assets/architecture.png" alt="Clinical Twin architecture diagram">
<div class="caption">
Figura: Architettura a microservizi della piattaforma Clinical Twin
</div>
</div>

<p>Flusso operativo principale:</p>

<div class="codeblock">
MRI → Segmentazione → Estrazione radiomica → Inferenza KNN → Embedding UMAP → Dashboard clinica
</div>

</div>


<h2>Architettura a microservizi</h2>

<div class="service-box">

<table>

<tr>
<th>Servizio</th>
<th>Tecnologia</th>
<th>Porta</th>
<th>Funzione</th>
</tr>

<tr>
<td>api_gateway</td>
<td>FastAPI, JWT</td>
<td>8000</td>
<td>Autenticazione utenti e routing richieste</td>
</tr>

<tr>
<td>orchestrator</td>
<td>FastAPI</td>
<td>8001</td>
<td>Gestione task asincroni pipeline</td>
</tr>

<tr>
<td>llm_service</td>
<td>FastAPI, Spatial RAG</td>
<td>8002</td>
<td>Assistente AI context-aware</td>
</tr>

<tr>
<td>model_service</td>
<td>FastAPI, MLflow</td>
<td>8003</td>
<td>Gestione modelli champion</td>
</tr>

<tr>
<td>inference_engine</td>
<td>R, Plumber</td>
<td>8004</td>
<td>Inferenza KNN e proiezione UMAP</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Nextflow, FreeSurfer</td>
<td>8005</td>
<td>Segmentazione MRI e radiomica</td>
</tr>

<tr>
<td>frontend</td>
<td>React, Plotly, NiiVue</td>
<td>5173</td>
<td>Dashboard clinica interattiva</td>
</tr>

</table>

</div>


<h2>Pipeline neuroimaging</h2>

<div class="service-box">

<p>
Le principali fasi della pipeline di preprocessing e analisi radiomica applicata alle immagini MRI strutturali.
</p>

<ul>
<li>preprocessing MRI volumetrica</li>
<li>segmentazione anatomica FreeSurfer / FastSurfer</li>
<li>estrazione ROI cerebrali</li>
<li>feature radiomiche PyRadiomics</li>
</ul>

</div>


<h2>inference_engine</h2>

<div class="service-box">

<p>
Implementa classificazione KNN e proiezione
UMAP 3D per rappresentare il paziente nello spazio latente diagnostico.
</p>

<ul>
<li>nearest neighbors clinici</li>
<li>cluster diagnostici</li>
<li>supporto decisionale interpretabile</li>
</ul>

</div>


<h2>Assistente AI context-aware</h2>

<div class="service-box">

<p>
Fornisce supporto interpretativo alle predizioni del modello integrando informazioni radiomiche, embedding UMAP e contesto clinico conversazionale.
</p>

<ul>
<li>interpretazione feature radiomiche</li>
<li>analisi posizione nello spazio UMAP</li>
<li>supporto explainability clinica</li>
<li>memoria conversazionale multi-turno</li>
</ul>

</div>



</div>

</body>
</html>