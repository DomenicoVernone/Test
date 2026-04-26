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

<p>
Questa guida descrive i passaggi essenziali per eseguire la prima analisi MRI con Clinical Twin dopo aver completato le fasi di installazione e configurazione dell’ambiente.
</p>

<div class="service-box">

<p>
Il workflow comprende l’avvio dei microservizi, la creazione del primo utente,
il caricamento della MRI e l’esecuzione automatica della pipeline di segmentazione,
estrazione radiomica e inferenza diagnostica.
</p>

</div>


<h2>1. Avvia lo stack Docker</h2>

<div class="service-box">

<p>
Avviare l’intera architettura tramite Docker Compose. Il comando inizializza
API Gateway, orchestrator, pipeline Nextflow, inference engine, servizio LLM
e dashboard clinica.
</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Attendere che tutti i container risultino attivi prima di procedere.
</p>

</div>


<h2>2. Accedi alla dashboard</h2>

<div class="service-box">

<p>
Una volta avviati i servizi, la dashboard React è disponibile tramite browser.
L’interfaccia consente upload MRI, visualizzazione dello spazio diagnostico
UMAP e interazione con l’assistente AI.
</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>3. Crea il primo utente</h2>

<div class="service-box">

<p>
Al primo avvio è necessario registrare un utente tramite Swagger UI esposto
dall’API Gateway. Questo passaggio abilita l’accesso autenticato alla dashboard.
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Eseguire la richiesta:</p>

<div class="codeblock">
POST /signup
</div>

<p>
Dopo la registrazione sarà possibile effettuare il login e avviare analisi MRI.
</p>

</div>


<h2>4. Carica una risonanza magnetica</h2>

<div class="service-box">

<p>
Dopo il login è possibile caricare una MRI strutturale cerebrale T1-weighted
per avviare automaticamente la pipeline di analisi.
</p>

<ul>
<li>aprire la sezione upload</li>
<li>selezionare un file .nii oppure .nii.gz</li>
<li>confermare l’elaborazione</li>
</ul>

<p>
Il dataset viene salvato nel volume condiviso Docker e registrato come task
asincrono gestito dall’orchestrator.
</p>

</div>


<h2>5. Esecuzione della pipeline</h2>

<div class="service-box">

<p>
Dopo l’upload la pipeline viene eseguita automaticamente tramite Nextflow
nel servizio nextflow_worker.
</p>

<p>Le principali fasi includono:</p>

<ul>
<li>preprocessing volumetrico MRI</li>
<li>segmentazione anatomica (FreeSurfer o FastSurfer)</li>
<li>estrazione ROI cerebrali</li>
<li>estrazione feature radiomiche con PyRadiomics</li>
<li>classificazione tramite KNN</li>
<li>proiezione nello spazio latente UMAP</li>
</ul>

</div>


<h2>6. Visualizza i risultati</h2>

<div class="service-box">

<p>
Al termine dell’elaborazione i risultati sono disponibili nella dashboard
clinica per l’analisi interattiva del caso paziente.
</p>

<ul>
<li>segmentazione multiplanare delle ROI (viewer NiiVue)</li>
<li>posizione del paziente nello spazio latente UMAP</li>
<li>classe diagnostica stimata</li>
<li>confidence score del classificatore</li>
<li>nearest neighbors clinicamente simili</li>
</ul>

</div>


<h2>7. Interroga l’assistente AI</h2>

<div class="service-box">

<p>
L’assistente AI context-aware supporta l’interpretazione dei risultati
radiomici combinando feature estratte, posizione nello spazio UMAP
e contesto clinico tramite approccio Spatial-RAG.
</p>

<ul>
<li>interpretazione delle feature radiomiche rilevanti</li>
<li>analisi della posizione nei cluster diagnostici</li>
<li>supporto alla lettura clinica del risultato predittivo</li>
</ul>

<p>
Questo modulo migliora l’interpretabilità del modello e facilita la
valutazione del caso paziente.
</p>

</div>


</div>

</body>

</html>