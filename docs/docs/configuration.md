<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Clinical Twin – Configuration</title>

<style>

/* ===== GLOBAL ===== */

body {
    margin: 0;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    display: flex;
    background: #f5f6f7;
}

/* ===== SIDEBAR ===== */

.sidebar {
    width: 300px;
    height: 100vh;
    background: linear-gradient(#2f6f95, #244f6a);
    color: white;
    position: fixed;
    padding: 20px;
    box-sizing: border-box;
}

.sidebar h2 {
    margin-top: 0;
}

.sidebar input {
    width: 100%;
    padding: 8px;
    border-radius: 6px;
    border: none;
    margin: 15px 0;
}

.sidebar ul {
    list-style: none;
    padding-left: 0;
}

.sidebar li {
    padding: 6px 0;
    opacity: 0.9;
}

.sidebar li.active {
    font-weight: bold;
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

/* ===== TABLE ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
}

th {
    background: #f0f0f0;
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

<!-- ===== SIDEBAR ===== -->



<!-- ===== MAIN CONTENT ===== -->

<div class="content">

<div class="breadcrumb">
Docs » Configuration
</div>

<h1>Configuration</h1>

<p>
Clinical Twin utilizza file di configurazione distribuiti tra i vari
microservizi per gestire autenticazione, pipeline neuroimaging,
inferenza diagnostica e integrazione con servizi esterni.
</p>


<h2>File .env principali</h2>

<div class="codeblock">
.env
api_gateway/.env
orchestrator/.env
model_service/.env
llm_service/.env
frontend/.env
</div>

<p>
Ogni servizio possiede un file di configurazione dedicato.
</p>


<h2>Variabili condivise (JWT)</h2>

<div class="service-box">

<table>
<tr>
<th>Variabile</th>
<th>Servizi</th>
<th>Descrizione</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Chiave condivisa per autenticazione JWT</td>
</tr>

</table>

</div>


<h2>Configurazione MLflow / DagsHub</h2>

<div class="service-box">

<table>
<tr>
<th>Variabile</th>
<th>Descrizione</th>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>URL tracking server MLflow</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_USERNAME</td>
<td>Username DagsHub</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>Token accesso Model Registry</td>
</tr>

<tr>
<td>REPO_OWNER</td>
<td>Owner repository DagsHub</td>
</tr>

<tr>
<td>REPO_NAME</td>
<td>Nome repository MLflow</td>
</tr>

</table>

</div>


<h2>Configurazione assistente AI</h2>

<div class="service-box">

<table>
<tr>
<th>Variabile</th>
<th>Descrizione</th>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>Chiave API per accesso al modello LLM</td>
</tr>

</table>

</div>


<h2>Configurazione GPU (opzionale)</h2>

<p>
Se disponibile una GPU NVIDIA, FastSurfer può utilizzare accelerazione CUDA.
</p>

<div class="codeblock">
MIG_DEVICE=
</div>

<p>
Su GPU partizionate impostare l’UUID della MIG instance.
Lasciare vuoto su sistemi CPU-only o GPU standard.
</p>


<h2>Configurazione volumi condivisi</h2>

<div class="codeblock">
HOST_SHARED_VOLUME_DIR=
</div>

<p>
Parametro richiesto solo su sistemi Linux bare-metal.
Su Docker Desktop (Windows/macOS) può rimanere vuoto.
</p>


<h2>Configurazione pipeline Nextflow</h2>

<p>
I parametri principali della pipeline sono definiti in:
</p>

<div class="codeblock">
nextflow_worker/nextflow/configs/nextflow.config
</div>


<div class="service-box">

<table>
<tr>
<th>Parametro</th>
<th>Descrizione</th>
</tr>

<tr>
<td>params.maxforks</td>
<td>Numero massimo processi paralleli</td>
</tr>

<tr>
<td>params.fastsurfer_threads</td>
<td>Thread CPU FastSurfer</td>
</tr>

<tr>
<td>params.fastsurfer_device</td>
<td>cpu oppure cuda</td>
</tr>

<tr>
<td>params.pyradiomics_jobs</td>
<td>Numero job radiomica paralleli</td>
</tr>

<tr>
<td>params.brain_segmenter</td>
<td>freesurfer oppure fastsurfer</td>
</tr>

</table>

</div>


<div class="nav-buttons">

<a class="button">⬅ Previous</a>
<a class="button">Next ➡</a>

</div>


<div class="footer">

© 2025 Clinical Twin Documentation  
Built with custom HTML/CSS (ReadTheDocs-style layout)

</div>

</div>

</body>
</html>