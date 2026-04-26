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
    white-space: pre-line;
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
Docs » Configuration
</div>

<h1>Configuration</h1>

<p>
Questa sezione descrive le principali variabili di configurazione utilizzate dai microservizi Clinical Twin per gestire autenticazione, accesso ai modelli, integrazione con servizi AI e parametri della pipeline radiomica.
</p>

<div class="service-box">

<p>
Clinical Twin utilizza file di configurazione distribuiti tra i diversi
microservizi della piattaforma per gestire autenticazione, orchestrazione
della pipeline neuroimaging, accesso ai modelli registrati e integrazione
con servizi di inferenza basati su modelli linguistici.
</p>

<p>
La corretta configurazione delle variabili di ambiente è necessaria per
garantire la comunicazione tra i servizi e il funzionamento completo
della pipeline radiomica.
</p>

</div>


<h2>File .env principali</h2>

<div class="service-box">

<p>
Ogni microservizio utilizza un file <code>.env</code> dedicato contenente
le variabili di configurazione specifiche per autenticazione, accesso
alle risorse e parametri operativi.
</p>

<div class="codeblock">
.env
api_gateway/.env
orchestrator/.env
model_service/.env
llm_service/.env
frontend/.env
</div>

<p>
Questi file devono essere configurati prima dell’avvio dello stack Docker.
</p>

</div>


<h2>Variabili condivise (JWT)</h2>

<div class="service-box">

<p>
Le variabili JWT permettono l’autenticazione sicura tra i microservizi
tramite token firmati digitalmente e garantiscono la protezione delle
richieste interne alla piattaforma.
</p>

<table>

<tr>
<th>Variabile</th>
<th>Servizi</th>
<th>Descrizione</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Chiave crittografica condivisa per la generazione e validazione dei token JWT tra i servizi</td>
</tr>

</table>

</div>


<h2>Configurazione MLflow / DagsHub</h2>

<div class="service-box">

<p>
Queste variabili consentono l’accesso al Model Registry MLflow ospitato
su DagsHub e permettono il recupero automatico del modello champion
utilizzato per l’inferenza diagnostica.
</p>

<table>

<tr>
<th>Variabile</th>
<th>Descrizione</th>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>Endpoint del server MLflow utilizzato per tracciare esperimenti e modelli</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_USERNAME</td>
<td>Username dell’account DagsHub per autenticazione al registry</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>Token di accesso al Model Registry remoto su DagsHub</td>
</tr>

<tr>
<td>REPO_OWNER</td>
<td>Nome utente o organizzazione proprietaria del repository MLflow</td>
</tr>

<tr>
<td>REPO_NAME</td>
<td>Nome del repository contenente i modelli registrati</td>
</tr>

</table>

</div>


<h2>Configurazione assistente AI</h2>

<div class="service-box">

<p>
L’assistente clinico context-aware utilizza modelli linguistici esterni
tramite API. La seguente variabile consente l’autenticazione al servizio
LLM utilizzato per supportare l’interpretazione dei risultati radiomici.
</p>

<table>

<tr>
<th>Variabile</th>
<th>Descrizione</th>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>Chiave API per l’accesso al modello linguistico utilizzato dal servizio AI</td>
</tr>

</table>

</div>


<h2>Configurazione GPU (opzionale)</h2>

<div class="service-box">

<p>
Se disponibile una GPU NVIDIA, FastSurfer può utilizzare accelerazione
CUDA per ridurre significativamente i tempi di segmentazione delle immagini MRI.
</p>

<div class="codeblock">
MIG_DEVICE=
</div>

<p>
Su sistemi con GPU partizionate (Multi-Instance GPU) è possibile specificare
l’identificativo della MIG instance assegnata al container. Lasciare vuoto
su sistemi CPU-only o GPU standard.
</p>

</div>


<h2>Configurazione volumi condivisi</h2>

<div class="service-box">

<p>
La variabile seguente definisce la directory host utilizzata per condividere
dataset MRI e output intermedi tra i container della pipeline Nextflow.
</p>

<div class="codeblock">
HOST_SHARED_VOLUME_DIR=
</div>

<p>
Questo parametro è richiesto principalmente su sistemi Linux bare-metal.
Su Docker Desktop (Windows/macOS) può rimanere non impostato.
</p>

</div>


<h2>Configurazione pipeline Nextflow</h2>

<div class="service-box">

<p>
I parametri principali della pipeline radiomica sono definiti nel file
di configurazione Nextflow. Queste impostazioni controllano parallelizzazione,
modalità di segmentazione e numero di job radiomici eseguiti simultaneamente.
</p>

<div class="codeblock">
nextflow_worker/nextflow/configs/nextflow.config
</div>

<table>

<tr>
<th>Parametro</th>
<th>Descrizione</th>
</tr>

<tr>
<td>params.maxforks</td>
<td>Numero massimo di processi paralleli eseguibili simultaneamente</td>
</tr>

<tr>
<td>params.fastsurfer_threads</td>
<td>Numero di thread CPU utilizzati durante la segmentazione FastSurfer</td>
</tr>

<tr>
<td>params.fastsurfer_device</td>
<td>Dispositivo di esecuzione: cpu oppure cuda</td>
</tr>

<tr>
<td>params.pyradiomics_jobs</td>
<td>Numero massimo di estrazioni radiomiche eseguite in parallelo</td>
</tr>

<tr>
<td>params.brain_segmenter</td>
<td>Selezione del segmentatore: freesurfer oppure fastsurfer</td>
</tr>

</table>

</div>


</div>

</body>
</html>