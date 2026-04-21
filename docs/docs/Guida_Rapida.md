<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Quickstart</title>

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
Docs » Quickstart
</div>

<h1>Quickstart</h1>

<div class="service-box">

<p>
Questa guida rapida descrive i passaggi necessari per eseguire la prima analisi
radiomica su una risonanza magnetica cerebrale T1-weighted utilizzando la
piattaforma Clinical Twin dopo l’installazione dello stack applicativo.
</p>

<p>
Il workflow comprende l’avvio dei microservizi, la registrazione dell’utente,
il caricamento della MRI e l’esecuzione automatizzata della pipeline di
segmentazione, estrazione radiomica e inferenza diagnostica.
</p>

</div>


<h2>1. Avvia lo stack Docker</h2>

<div class="service-box">

<p>
Avviare l’intera architettura a microservizi tramite Docker Compose.
Questo comando inizializza API Gateway, orchestrator, pipeline Nextflow,
motore di inferenza, servizio LLM e dashboard clinica.
</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Attendere il completamento dell’avvio dei container prima di procedere
alle fasi successive.
</p>

</div>


<h2>2. Accedi alla dashboard</h2>

<div class="service-box">

<p>
Una volta avviati i servizi, l’interfaccia clinica React sarà disponibile
tramite browser web. La dashboard consente l’upload delle immagini MRI,
la visualizzazione dello spazio diagnostico e l’interazione con
l’assistente AI.
</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>3. Crea il primo utente</h2>

<div class="service-box">

<p>
Al primo avvio della piattaforma è necessario registrare un utente tramite
Swagger UI esposto dall’API Gateway. Questa operazione consente di ottenere
le credenziali di accesso alla dashboard.
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Eseguire la richiesta:</p>

<div class="codeblock">
POST /signup
</div>

<p>
Dopo la registrazione sarà possibile autenticarsi ed eseguire nuove analisi MRI.
</p>

</div>


<h2>4. Carica una risonanza magnetica</h2>

<div class="service-box">

<p>
Dopo il login nella dashboard clinica è possibile caricare una risonanza
magnetica strutturale cerebrale per avviare la pipeline radiomica.
</p>

<ul>
<li>aprire la sezione upload</li>
<li>selezionare un file MRI in formato .nii oppure .nii.gz</li>
<li>avviare l’elaborazione</li>
</ul>

<p>
Il dataset viene salvato nel volume condiviso Docker e registrato come
task asincrono gestito dall’orchestrator.
</p>

</div>


<h2>5. Avvia la pipeline di segmentazione</h2>

<div class="service-box">

<p>
Dopo l’upload, la pipeline neuroimaging viene eseguita automaticamente
tramite Nextflow all’interno del servizio nextflow_worker.
</p>

<p>Le principali fasi computazionali includono:</p>

<ul>
<li>preprocessing volumetrico MRI</li>
<li>segmentazione anatomica (FreeSurfer o FastSurfer)</li>
<li>estrazione delle regioni cerebrali (ROI)</li>
<li>estrazione feature radiomiche con PyRadiomics</li>
<li>inferenza statistica tramite classificatore KNN</li>
<li>proiezione nello spazio latente diagnostico UMAP</li>
</ul>

</div>


<h2>6. Visualizza i risultati</h2>

<div class="service-box">

<p>
Al termine dell’elaborazione, i risultati vengono resi disponibili nella
dashboard clinica per l’analisi interattiva del caso paziente.
</p>

<ul>
<li>segmentazione multiplanare delle ROI cerebrali (viewer NiiVue)</li>
<li>coordinate del paziente nello spazio latente UMAP</li>
<li>classe diagnostica stimata</li>
<li>confidence score del classificatore</li>
<li>nearest neighbors clinicamente simili</li>
</ul>

</div>


<h2>7. Interroga l’assistente AI</h2>

<div class="service-box">

<p>
L’assistente AI context-aware consente di interpretare i risultati radiomici
e la posizione del paziente nello spazio diagnostico tramite analisi
Spatial-RAG.
</p>

<ul>
<li>interpretazione delle feature radiomiche</li>
<li>analisi della posizione nel cluster diagnostico UMAP</li>
<li>supporto decisionale clinico contestualizzato</li>
</ul>

<p>
Questo modulo migliora l’interpretabilità del modello e supporta il processo
decisionale medico.
</p>

</div>



</div>

</body>

</html>