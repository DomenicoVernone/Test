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

<div class="content">

<div class="breadcrumb">
Docs » System Architecture
</div>

<h1>System Architecture</h1>

<h2>Visione generale</h2>

<div class="service-box">

<p>
La piattaforma MLOps è progettata come un sistema distribuito basato su
microservizi containerizzati orchestrati tramite Docker Compose.
L’architettura separa chiaramente le responsabilità tra preprocessing
dei dati, orchestrazione dei workflow, inferenza statistica e
visualizzazione clinica.
</p>

<p>
Questo approccio consente:
</p>

<ul>
<li>scalabilità dei singoli componenti</li>
<li>isolamento delle dipendenze</li>
<li>riproducibilità delle analisi radiomiche</li>
<li>facilità di estensione del sistema</li>
</ul>

</div>

<h2>Flusso dati end-to-end</h2>

<div class="service-box">

<p>
Il sistema implementa un flusso dati sequenziale orchestrato tra i
microservizi, dalla ricezione della MRI fino alla produzione del risultato
diagnostico e della sua interpretazione.
</p>

<div class="codeblock">
Frontend
  ↓
API Gateway (autenticazione JWT)
  ↓
Orchestrator (gestione task)
  ↓
Nextflow Worker (pipeline radiomica)
  ↓
Radiomics Features (CSV)
  ↓
Inference Engine (KNN + UMAP)
  ↓
LLM Service (explainability)
  ↓
Frontend (visualizzazione clinica)
</div>

<p>
Ogni passaggio è progettato per essere indipendente e comunicare tramite
API REST o file condivisi, garantendo modularità e fault isolation.
</p>

</div>

<h2>Struttura dei microservizi</h2>

<div class="service-box">

<table>

<tr>
<th>Servizio</th>
<th>Ruolo</th>
<th>Tecnologia</th>
</tr>

<tr>
<td>api_gateway</td>
<td>Autenticazione, autorizzazione e routing richieste</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Gestione workflow asincroni e stato pipeline</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Esecuzione pipeline neuroimaging e radiomica</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Inferenza diagnostica e embedding UMAP</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>llm_service</td>
<td>Explainability e interpretazione AI</td>
<td>FastAPI, LLM API</td>
</tr>

<tr>
<td>model_service</td>
<td>Gestione modelli ML (registry, versioning)</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>frontend</td>
<td>Interfaccia utente e visualizzazione clinica</td>
<td>React</td>
</tr>

</table>

</div>

<h2>Ruoli e responsabilità dei servizi</h2>

<div class="service-box">

<h3>api_gateway</h3>
<p>
Costituisce il punto di ingresso unico del sistema. Gestisce autenticazione
utente tramite JWT e inoltra le richieste ai servizi interni.
</p>

<h3>orchestrator</h3>
<p>
Coordina l’esecuzione della pipeline MRI. Mantiene lo stato dei task
(pending, running, completed, failed) e gestisce la comunicazione con
il nextflow_worker.
</p>

<h3>nextflow_worker</h3>
<p>
Esegue la pipeline di preprocessing e radiomica utilizzando Nextflow.
Produce feature radiomiche strutturate a partire da immagini MRI.
</p>

<h3>inference_engine</h3>
<p>
Esegue l’inferenza diagnostica utilizzando le feature radiomiche.
Implementa:
</p>

<ul>
<li>classificazione KNN</li>
<li>proiezione nello spazio latente UMAP</li>
</ul>

<p>
Questo servizio rappresenta il cuore computazionale della diagnosi.
</p>

<h3>model_service</h3>
<p>
Gestisce il Model Registry MLflow e fornisce accesso ai modelli
versionati. Non esegue direttamente inferenza, ma prepara i modelli
per l’utilizzo da parte dell’inference_engine.
</p>

<h3>llm_service</h3>
<p>
Fornisce interpretazione clinica delle predizioni. Viene invocato:
</p>

<ul>
<li>dopo l’inferenza</li>
<li>su richiesta dell’utente (chat)</li>
</ul>

<p>
Utilizza feature radiomiche, coordinate UMAP e contesto diagnostico
per generare spiegazioni contestualizzate.
</p>

<h3>frontend</h3>
<p>
Fornisce interfaccia utente per:
</p>

<ul>
<li>upload MRI</li>
<li>visualizzazione segmentazioni</li>
<li>esplorazione spazio UMAP</li>
<li>interazione con assistente AI</li>
</ul>

</div>

<h2>Comunicazione tra servizi</h2>

<div class="service-box">

<p>
I microservizi comunicano tramite:
</p>

<ul>
<li>API REST (HTTP/JSON)</li>
<li>volumi condivisi Docker (file MRI e output pipeline)</li>
</ul>

<p>
Questa architettura ibrida consente:
</p>

<ul>
<li>trasferimento efficiente di file voluminosi (MRI)</li>
<li>interoperabilità tra servizi eterogenei (Python, R)</li>
</ul>

</div>

<h2>Gestione dello stato</h2>

<div class="service-box">

<p>
Lo stato delle analisi MRI è gestito dal servizio orchestrator.
Ogni task attraversa il seguente ciclo:
</p>

<div class="codeblock">
pending → running → completed / failed
</div>

<p>
Questo approccio consente monitoraggio e gestione robusta dei workflow,
inclusa la propagazione degli errori tra i servizi.
</p>

</div>

<h2>Scelte architetturali</h2>

<div class="service-box">

<h3>Microservizi</h3>
<p>
La decomposizione in microservizi consente indipendenza di sviluppo,
deploy e scaling dei singoli componenti.
</p>

<h3>Containerizzazione</h3>
<p>
L’utilizzo di Docker garantisce isolamento delle dipendenze e
riproducibilità dell’ambiente di esecuzione.
</p>

<h3>Nextflow per pipeline</h3>
<p>
Nextflow consente gestione deterministica e parallela dei workflow
scientifici, fondamentale per applicazioni radiomiche.
</p>

<h3>Separazione inferenza / modelli</h3>
<p>
La distinzione tra model_service e inference_engine permette
gestione indipendente del ciclo di vita dei modelli e della logica
di inferenza.
</p>

</div>

<h2>Scalabilità e estendibilità</h2>

<div class="service-box">

<p>
L’architettura è progettata per supportare:
</p>

<ul>
<li>integrazione di nuovi modelli diagnostici</li>
<li>sostituzione dell’inference engine</li>
<li>aggiunta di nuovi moduli AI</li>
<li>scaling orizzontale dei servizi</li>
</ul>

<p>
Questo rende la piattaforma adatta sia a contesti di ricerca che
a scenari di produzione su larga scala.
</p>

</div>

</div>

</body>

</html>
