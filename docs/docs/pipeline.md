<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Clinical Twin – Pipeline Workflow</title>

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

/* ===== CODE BLOCK ===== */

.codeblock {
    background: #eeeeee;
    padding: 14px;
    border-radius: 6px;
    font-family: monospace;
    margin: 15px 0;
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

<!-- ===== MAIN CONTENT ===== -->

<div class="content">

<div class="breadcrumb">
Docs » Pipeline Workflow
</div>

<h1>Pipeline Workflow</h1>

<p>
La pipeline di Clinical Twin implementa un workflow automatizzato di analisi
radiomica su risonanze magnetiche cerebrali T1-weighted finalizzato alla
diagnosi differenziale delle varianti di Frontotemporal Dementia (FTD).
</p>

<p>
L’intero processo è orchestrato dal microservizio <b>orchestrator</b> e
eseguito tramite <b>Nextflow</b> all’interno del servizio
<b>nextflow_worker</b>.
</p>


<h2>Panoramica della pipeline</h2>

<div class="codeblock">
MRI → Preprocessing → Segmentazione → Estrazione ROI → Radiomics → Inferenza KNN → Embedding UMAP → Dashboard
</div>


<h2>1. Upload della MRI</h2>

<p>
L’utente carica una risonanza magnetica strutturale cerebrale tramite
l’interfaccia web. I formati supportati sono:
</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
Il file viene salvato nel volume condiviso del sistema e registrato come task
asincrono.
</p>


<h2>2. Preprocessing volumetrico</h2>

<p>
La pipeline esegue operazioni preliminari necessarie alla segmentazione:
</p>

<ul>
<li>normalizzazione dell’intensità</li>
<li>ricampionamento volumetrico</li>
<li>allineamento spaziale</li>
<li>verifica integrità del volume MRI</li>
</ul>


<h2>3. Segmentazione anatomica</h2>

<p>
La segmentazione cerebrale viene effettuata utilizzando:
</p>

<ul>
<li>FreeSurfer (modalità CPU)</li>
<li>FastSurfer (modalità GPU opzionale)</li>
</ul>

<p>
Il risultato consiste nella parcellizzazione della corteccia cerebrale in
regioni anatomiche standardizzate (ROI).
</p>


<h2>4. Estrazione delle ROI cerebrali</h2>

<p>
Le regioni segmentate vengono mappate utilizzando la tabella:
</p>

<div class="codeblock">
ROI_labels.tsv
</div>

<p>
Questa fase consente l’associazione tra etichette anatomiche e volumi segmentati.
</p>


<h2>5. Estrazione feature radiomiche</h2>

<p>
Le feature radiomiche vengono estratte tramite PyRadiomics utilizzando il file
di configurazione:
</p>

<div class="codeblock">
pyradiomics.yaml
</div>

<p>
Le principali categorie di feature includono:
</p>

<ul>
<li>first-order statistics</li>
<li>GLCM texture features</li>
<li>GLRLM features</li>
<li>GLSZM features</li>
<li>shape descriptors</li>
</ul>


<h2>6. Inferenza statistica</h2>

<p>
Le feature radiomiche estratte vengono inviate al servizio
<b>inference_engine</b>, che esegue:
</p>

<ul>
<li>classificazione tramite algoritmo KNN</li>
<li>calcolo similarità con pazienti del dataset di riferimento</li>
<li>stima della classe diagnostica</li>
</ul>


<h2>7. Proiezione nello spazio latente UMAP</h2>

<p>
Le feature vengono proiettate in uno spazio tridimensionale utilizzando UMAP
per consentire:
</p>

<ul>
<li>visualizzazione della distribuzione dei pazienti</li>
<li>analisi dei cluster diagnostici</li>
<li>identificazione dei nearest neighbors clinici</li>
</ul>


<h2>8. Visualizzazione dei risultati</h2>

<p>
I risultati finali sono disponibili nella dashboard React e includono:
</p>

<ul>
<li>segmentazione multiplanare delle ROI (NiiVue)</li>
<li>posizione del paziente nello spazio UMAP</li>
<li>classe diagnostica stimata</li>
<li>confidence score</li>
<li>nearest neighbors clinici</li>
</ul>


<h2>9. Interpretazione tramite assistente AI</h2>

<p>
L’assistente AI context-aware supporta l’interpretazione dei risultati
radiomici e della posizione del paziente nello spazio latente, fornendo
spiegazioni clinicamente rilevanti.
</p>


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