<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Deployment</title>

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

<h1>Deployment della piattaforma MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
Questa sezione descrive le modalità di distribuzione della piattaforma
MLOps in diversi contesti operativi, dal testing locale fino a
infrastrutture server dedicate.
</p>

<p>
L’intero sistema è progettato per essere eseguito tramite container Docker,
garantendo isolamento delle dipendenze, portabilità e riproducibilità
dell’ambiente di esecuzione.
</p>

</div>

<div class="section">
<h2>2. Contesto architetturale</h2>

<p>
La piattaforma è basata su un’architettura a microservizi descritta
in dettaglio nella sezione <b>System Architecture</b>.
</p>

<p>
Nel contesto del deployment, i servizi vengono orchestrati tramite Docker Compose
e comunicano attraverso API REST e volumi condivisi per la gestione
dei dati MRI e degli output della pipeline.
</p>

</div>

<div class="section">
<h2>3. Deployment locale (sviluppo)</h2>

<p>
La modalità locale è utilizzata per sviluppo, debugging e test funzionali.
</p>

<p>Compatibilità:</p>

<ul>
<li>Windows (WSL2)</li>
<li>macOS</li>
<li>Linux</li>
</ul>

<p>Avvio dello stack:</p>

<pre>
docker compose up -d --build
</pre>

<p>
Questo comando costruisce le immagini e avvia tutti i microservizi.
</p>

<p>Accesso:</p>

<pre>
Frontend → http://localhost:5173  
API → http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>4. Deployment su server Linux</h2>

<p>
Configurazione consigliata per esecuzione su dataset MRI di grandi dimensioni.
</p>

<p>Prerequisiti:</p>

<ul>
<li>Docker Engine installato</li>
<li>Docker Compose</li>
<li>CPU multicore</li>
<li>≥16 GB RAM consigliati</li>
</ul>

<p>Configurazione volume condiviso:</p>

<pre>
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</pre>

<p>
Questa directory viene utilizzata per condividere dati tra container
durante l’esecuzione della pipeline.
</p>

<p>Avvio servizi:</p>

<pre>
docker compose up -d
</pre>

</div>

<div class="section">
<h2>5. Deployment con GPU NVIDIA</h2>

<p>
L’utilizzo di GPU NVIDIA consente di accelerare la segmentazione
anatomica tramite FastSurfer, riducendo significativamente i tempi
di elaborazione.
</p>

<p>Prerequisiti:</p>

<ul>
<li>Driver NVIDIA aggiornati</li>
<li>CUDA compatibile</li>
<li>NVIDIA Container Toolkit</li>
</ul>

<p>Verifica disponibilità GPU:</p>

<pre>
nvidia-smi
</pre>

<p>Abilitazione GPU nella pipeline:</p>

<pre>
params.fastsurfer_device=cuda
</pre>

<p>
Questo parametro abilita l’utilizzo della GPU nei processi di segmentazione.
</p>

</div>

<div class="section">
<h2>6. Deployment con GPU MIG (Multi-Instance GPU)</h2>

<p>
Su sistemi HPC multi-utente è possibile utilizzare la tecnologia
Multi-Instance GPU (MIG) per suddividere una GPU NVIDIA in più
istanze isolate.
</p>

<p>
Questo approccio consente di assegnare una porzione dedicata di GPU
a ciascun job della pipeline, migliorando l’isolamento delle risorse
e la gestione dei carichi concorrenti.
</p>

<p>
Nel contesto della pipeline radiomica, MIG può essere utilizzato per:
</p>

<ul>
<li>eseguire più segmentazioni in parallelo</li>
<li>evitare interferenze tra job concorrenti</li>
<li>ottimizzare l’utilizzo delle risorse GPU</li>
</ul>

<p>
Configurazione variabile ambiente:
</p>

<pre>
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</pre>

<p>
Questa variabile identifica la specifica istanza GPU assegnata al container.
</p>

<p>
Su sistemi senza partizionamento GPU o in modalità CPU-only,
la variabile può essere lasciata vuota.
</p>

</div>

<div class="section">
<h2>7. Deployment multi-ambiente</h2>

<p>
Il sistema supporta diversi ambienti operativi:
</p>

<ul>
<li><b>development</b> → sviluppo e debugging</li>
<li><b>staging</b> → validazione pre-produzione</li>
<li><b>production</b> → utilizzo su larga scala</li>
</ul>

<p>
Le differenze principali riguardano:
</p>

<ul>
<li>configurazione logging</li>
<li>gestione delle credenziali</li>
<li>allocazione delle risorse hardware</li>
</ul>

</div>

<div class="section">
<h2>8. Build immagini pipeline</h2>

<p>
Prima dell’esecuzione della pipeline è necessario costruire le immagini
Docker utilizzate dai processi Nextflow.
</p>

<pre>
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</pre>

<p>
Queste immagini vengono richiamate dinamicamente durante l’esecuzione
della pipeline.
</p>

</div>

<div class="section">
<h2>9. Gestione volumi e dati</h2>

<p>
I dati MRI e gli output della pipeline sono gestiti tramite volumi Docker
condivisi tra i servizi.
</p>

<ul>
<li>input MRI caricati dal frontend</li>
<li>output radiomici generati dalla pipeline</li>
<li>file intermedi di processamento</li>
</ul>

<p>
Questo approccio evita il trasferimento di file voluminosi tramite API,
migliorando le performance del sistema.
</p>

</div>

<div class="section">
<h2>10. Scalabilità</h2>

<p>
L’architettura consente scaling indipendente dei servizi:
</p>

<ul>
<li>parallelizzazione pipeline Nextflow</li>
<li>esecuzione concorrente di più analisi MRI</li>
<li>scaling dell’inference engine</li>
</ul>

<p>
Il sistema può essere esteso per gestire carichi elevati
in ambienti di ricerca o produzione.
</p>

</div>

<div class="section">
<h2>11. Logging e monitoraggio</h2>

<p>
Il sistema utilizza diversi livelli di logging:
</p>

<ul>
<li>log Docker per i microservizi</li>
<li>log Nextflow per la pipeline</li>
<li>stato task gestito dall’orchestrator</li>
</ul>

<p>
Questo consente monitoraggio completo e debugging efficace.
</p>

</div>

<div class="section">
<h2>12. Sicurezza</h2>

<p>
Le credenziali sensibili sono gestite tramite variabili ambiente:
</p>

<ul>
<li>SECRET_KEY</li>
<li>DAGSHUB_TOKEN</li>
<li>GROQ_API_KEY</li>
</ul>

<p>
Le chiavi non devono essere incluse nel codice sorgente e devono essere
configurate tramite file .env.
</p>

</div>

<div class="section">
<h2>13. Conclusioni</h2>

<p>
Il deployment basato su container consente di eseguire la piattaforma
in modo consistente su ambienti diversi, mantenendo isolamento e
riproducibilità.
</p>

<p>
L’architettura è progettata per supportare sia utilizzo locale che
deployment su infrastrutture dedicate, rendendo il sistema scalabile
e pronto per scenari reali.
</p>

</div>

</div>

</body>

</html>
