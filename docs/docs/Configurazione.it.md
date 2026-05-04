<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Configuration</title>

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

<h1>Configurazione della piattaforma MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
La configurazione della piattaforma MLOps è basata su variabili
di ambiente distribuite tra i microservizi.
</p>

<p>
Questo approccio consente di separare la logica applicativa
dai parametri operativi, facilitando il deployment in ambienti
diversi (development, staging, production).
</p>

</div>

<div class="section">
<h2>2. File di configurazione</h2>

<p>
Ogni microservizio utilizza un file <code>.env</code> dedicato
per la gestione delle variabili di ambiente.
</p>

<pre>
.env
api_gateway/.env
orchestrator/.env
model_service/.env
llm_service/.env
frontend/.env
</pre>

<p>
Questi file devono essere configurati prima dell’avvio del sistema.
</p>

</div>

<div class="section">
<h2>3. Variabili principali</h2>

<p>
Le seguenti variabili rappresentano i parametri fondamentali per
l’autenticazione tra microservizi, l’accesso ai modelli e
l’integrazione con servizi AI.
</p>

<table>

<tr>
<th>Variabile</th>
<th>Servizio</th>
<th>Descrizione</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Chiave condivisa per la generazione e validazione dei token JWT tra i microservizi</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>llm_service</td>
<td>Chiave di accesso al servizio LLM utilizzato dall’assistente AI context-aware</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>model_service</td>
<td>Endpoint del server MLflow per il recupero dei modelli registrati</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>model_service</td>
<td>Token di autenticazione per l’accesso al Model Registry ospitato su DagsHub</td>
</tr>

</table>

</div>

<div class="section">
<h2>4. Configurazione MLflow / Model Registry</h2>

<p>
Il servizio <b>model_service</b> utilizza MLflow per la gestione
dei modelli di machine learning.
</p>

<p>
Le variabili configurate consentono:
</p>

<ul>
<li>connessione al tracking server</li>
<li>download del modello champion</li>
<li>versionamento dei modelli</li>
</ul>

<p>
Questa integrazione permette di separare il ciclo di vita dei modelli
dalla logica di inferenza.
</p>

</div>

<div class="section">
<h2>5. Configurazione assistente AI</h2>

<p>
Il servizio <b>llm_service</b> utilizza un modello linguistico esterno
per generare interpretazioni cliniche.
</p>

<p>
La variabile <code>GROQ_API_KEY</code> consente l’autenticazione al servizio
LLM e deve essere configurata correttamente per abilitare l’assistente AI.
</p>

</div>

<div class="section">
<h2>6. Configurazione GPU (opzionale)</h2>

<p>
Se disponibile una GPU NVIDIA, è possibile accelerare la pipeline
di segmentazione utilizzando FastSurfer in modalità CUDA.
</p>

<pre>
params.fastsurfer_device=cuda
</pre>

<p>
Su sistemi CPU-only questo parametro deve essere impostato su:
</p>

<pre>
params.fastsurfer_device=cpu
</pre>

</div>

<div class="section">
<h2>7. Configurazione GPU MIG</h2>

<p>
Su sistemi HPC multi-utente è possibile utilizzare GPU partizionate
tramite tecnologia Multi-Instance GPU (MIG).
</p>

<p>
Questa configurazione consente di assegnare una specifica istanza GPU
a ciascun job della pipeline.
</p>

<pre>
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</pre>

<p>
Se non si utilizza MIG, la variabile può essere lasciata vuota.
</p>

</div>

<div class="section">
<h2>8. Configurazione volumi condivisi</h2>

<p>
Il sistema utilizza una directory condivisa per lo scambio
di dati tra microservizi.
</p>

<pre>
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</pre>

<p>
Questa directory contiene:
</p>

<ul>
<li>dataset MRI</li>
<li>output radiomici</li>
<li>file intermedi</li>
</ul>

</div>

<div class="section">
<h2>9. Configurazione pipeline Nextflow</h2>

<p>
I parametri della pipeline sono definiti nel file:
</p>

<pre>
nextflow_worker/nextflow/configs/nextflow.config
</pre>

<table>

<tr>
<th>Parametro</th>
<th>Descrizione</th>
</tr>

<tr>
<td>maxforks</td>
<td>Numero massimo di processi paralleli</td>
</tr>

<tr>
<td>pyradiomics_jobs</td>
<td>Numero di job radiomici simultanei</td>
</tr>

<tr>
<td>fastsurfer_threads</td>
<td>Numero di thread CPU utilizzati</td>
</tr>

<tr>
<td>brain_segmenter</td>
<td>Selezione segmentatore (freesurfer / fastsurfer)</td>
</tr>

</table>

</div>

<div class="section">
<h2>10. Conclusioni</h2>

<p>
La configurazione della piattaforma MLOps consente un’elevata
flessibilità operativa, permettendo di adattare il sistema
a diversi ambienti e requisiti hardware.
</p>

<p>
La separazione tra configurazione e logica applicativa facilita
il deployment e garantisce una gestione più sicura e scalabile
dell’infrastruttura.
</p>

</div>

</div>

</body>

</html>
