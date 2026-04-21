<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Deployment</title>

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
Docs » Deployment
</div>

<h1>Deployment</h1>

<div class="service-box">

<p>
Clinical Twin può essere distribuito in diversi ambienti operativi,
dal computer locale per attività di sviluppo fino a server GPU dedicati
per l’esecuzione efficiente della pipeline neuroimaging su dataset clinici.
</p>

<p>
L’architettura containerizzata basata su Docker Compose garantisce
portabilità, riproducibilità sperimentale e scalabilità computazionale.
</p>

</div>


<h2>Deployment locale (Docker Desktop)</h2>

<div class="service-box">

<p>
Configurazione consigliata per sviluppo, test funzionali e validazione
della pipeline su singoli dataset MRI.
</p>

<p>Compatibile con:</p>

<ul>
<li>Windows (tramite WSL2)</li>
<li>macOS</li>
<li>Linux</li>
</ul>

<p>Avvio completo dello stack applicativo:</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Questo comando inizializza API Gateway, orchestrator, Nextflow worker,
motore di inferenza, servizio LLM e dashboard React.
</p>

<p>Accesso alla dashboard clinica:</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>Deployment su server Linux</h2>

<div class="service-box">

<p>
Configurazione consigliata per ambienti di laboratorio, infrastrutture
di ricerca o server dipartimentali dedicati all’elaborazione radiomica.
</p>

<p>Prerequisiti hardware/software:</p>

<ul>
<li>Docker Engine installato</li>
<li>Docker Compose</li>
<li>CPU multicore</li>
<li>≥16 GB RAM consigliati</li>
</ul>

<p>
Configurare la directory condivisa utilizzata dalla pipeline Nextflow
per l’accesso ai volumi MRI:
</p>

<div class="codeblock">
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</div>

<p>Avvio servizi:</p>

<div class="codeblock">
docker compose up -d
</div>

</div>


<h2>Deployment con GPU NVIDIA</h2>

<div class="service-box">

<p>
L’utilizzo di GPU NVIDIA consente l’accelerazione della segmentazione
cerebrale tramite FastSurfer, riducendo significativamente i tempi di
elaborazione rispetto alla modalità CPU.
</p>

<p>Prerequisiti:</p>

<ul>
<li>Driver NVIDIA aggiornati</li>
<li>CUDA Toolkit compatibile</li>
<li>NVIDIA Container Toolkit</li>
</ul>

<p>Verifica disponibilità GPU:</p>

<div class="codeblock">
nvidia-smi
</div>

<p>
Abilitazione accelerazione GPU nella pipeline:
</p>

<div class="codeblock">
params.fastsurfer_device=cuda
</div>

</div>


<h2>Deployment con GPU MIG (Multi-Instance GPU)</h2>

<div class="service-box">

<p>
Su sistemi HPC o server multi-utente dotati di GPU partizionabili,
è possibile assegnare una specifica MIG instance alla pipeline
Clinical Twin per isolare le risorse computazionali.
</p>

<p>Configurazione variabile ambiente:</p>

<div class="codeblock">
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</div>

<p>
Lasciare il parametro vuoto su sistemi senza partizionamento GPU.
</p>

</div>


<h2>Deployment pipeline Nextflow</h2>

<div class="service-box">

<p>
Clinical Twin utilizza un modello Docker-out-of-Docker (DooD) per
l’esecuzione modulare dei componenti della pipeline neuroimaging.
</p>

<p>
Prima dell’avvio della pipeline è necessario costruire le immagini
container utilizzate dai worker Nextflow:
</p>

<div class="codeblock">
docker build -t clinical-freesurfer -f nextflow_worker/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/pyradiomics.dockerfile nextflow_worker/
</div>

<p>
Queste immagini includono gli strumenti di segmentazione anatomica,
preprocessing MRI ed estrazione feature radiomiche.
</p>

</div>


<h2>Deployment in produzione (consigliato)</h2>

<div class="service-box">

<p>
Per ambienti clinici o dataset di grandi dimensioni è consigliata una
configurazione server dedicata con accelerazione GPU.
</p>

<p>Configurazione suggerita:</p>

<ul>
<li>server Linux dedicato</li>
<li>GPU NVIDIA compatibile CUDA</li>
<li>Docker Engine</li>
<li>volume condiviso persistente per dataset MRI</li>
<li>sistema di backup per dataset radiomici e modelli</li>
</ul>

<p>Architettura logica dei servizi:</p>

<div class="codeblock">
Frontend → API Gateway → Orchestrator → Nextflow Worker → Inference Engine → LLM Service
</div>

<p>
Questa configurazione garantisce scalabilità della pipeline,
separazione dei microservizi e supporto a workflow clinico-radiomici
riproducibili.
</p>

</div>

</div>

</body>

</html>