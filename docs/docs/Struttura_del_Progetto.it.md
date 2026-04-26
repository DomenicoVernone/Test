<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Clinical Twin – Project Structure</title>

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

.sidebar h2 { margin-top: 0; }

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
}

h2 {
    margin-top: 40px;
    font-size: 26px;
}

/* ===== BLOCK ===== */

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
    padding: 18px;
    border-radius: 6px;
    font-family: monospace;
    margin: 20px 0;
    white-space: pre;
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
Docs » Project Structure
</div>

<h1>Project Structure</h1>

<p>
Questa sezione descrive l’organizzazione del repository Clinical Twin e il ruolo delle principali directory che compongono l’architettura a microservizi della piattaforma.
</p>

<p>
La separazione dei componenti in moduli indipendenti facilita manutenzione del codice, scalabilità della pipeline MRI e riproducibilità delle analisi radiomiche.
</p>


<h2>Struttura generale del repository</h2>

<p>
Il repository è organizzato in directory dedicate ai singoli microservizi e ai componenti della pipeline computazionale.
</p>

<div class="codeblock">
Tesi-FTD/
│
├── docker-compose.yml
├── .env.example
├── docs/
│   └── architecture.png
│
├── api_gateway/
├── orchestrator/
├── model_service/
├── llm_service/
├── inference_engine/
├── nextflow_worker/
└── frontend/
</div>


<h2>api_gateway</h2>

<div class="service-box">

<p>
Gestisce autenticazione utenti, generazione token JWT e accesso sicuro agli endpoint backend della piattaforma.
</p>

<ul>
<li>registrazione utenti</li>
<li>login JWT</li>
<li>validazione token</li>
<li>protezione endpoint REST</li>
</ul>

</div>


<h2>orchestrator</h2>

<div class="service-box">

<p>
Coordina l’esecuzione asincrona delle analisi MRI, creando task pipeline e invocando l’esecuzione Nextflow tramite il servizio nextflow_worker.
</p>

<ul>
<li>gestione task asincroni</li>
<li>monitoraggio stato pipeline</li>
<li>invocazione Nextflow</li>
<li>sincronizzazione microservizi backend</li>
</ul>

</div>


<h2>model_service</h2>

<div class="service-box">

<p>
Gestisce l’accesso al Model Registry MLflow ospitato su DagsHub e prepara il modello diagnostico utilizzato durante l’inferenza.
</p>

<ul>
<li>download champion model</li>
<li>versioning modelli</li>
<li>integrazione Model Registry</li>
<li>preparazione input per inferenza</li>
</ul>

</div>


<h2>llm_service</h2>

<div class="service-box">

<p>
Implementa l’assistente AI context-aware basato su Spatial RAG per supportare interpretazione clinica e explainability dei risultati diagnostici.
</p>

<ul>
<li>interpretazione feature radiomiche</li>
<li>analisi cluster diagnostici UMAP</li>
<li>memoria conversazionale multi-turno</li>
<li>interazione clinica guidata</li>
</ul>

</div>


<h2>inference_engine</h2>

<div class="service-box">

<p>
Motore statistico implementato in R tramite Plumber che esegue classificazione KNN e proiezione del paziente nello spazio latente UMAP tridimensionale.
</p>

<ul>
<li>classificazione KNN</li>
<li>calcolo similarità clinica</li>
<li>embedding UMAP 3D</li>
<li>identificazione nearest neighbors</li>
</ul>

</div>


<h2>nextflow_worker</h2>

<div class="service-box">

<p>
Esegue la pipeline MRI strutturale tramite Nextflow utilizzando container dedicati per segmentazione anatomica ed estrazione delle feature radiomiche.
</p>

<ul>
<li>segmentazione FreeSurfer / FastSurfer</li>
<li>estrazione ROI cerebrali</li>
<li>estrazione feature radiomiche PyRadiomics</li>
<li>workflow Nextflow containerizzato</li>
</ul>

</div>


<h2>frontend</h2>

<div class="service-box">

<p>
Dashboard clinica sviluppata in React per la gestione delle analisi MRI e la visualizzazione interattiva dei risultati diagnostici.
</p>

<ul>
<li>upload MRI</li>
<li>viewer multiplanare (NiiVue)</li>
<li>visualizzazione spazio latente UMAP</li>
<li>storico analisi</li>
<li>assistente AI integrato</li>
</ul>

</div>


<h2>Directory docs</h2>

<div class="service-box">

<p>
Contiene la documentazione tecnica della piattaforma, inclusi diagrammi architetturali, manuale utente e descrizione della pipeline MRI.
</p>

<ul>
<li>diagramma architetturale</li>
<li>manuale utente</li>
<li>documentazione pipeline</li>
</ul>

</div>


</div>

</body>
</html>