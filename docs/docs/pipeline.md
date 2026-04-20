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
Docs » Pipeline Workflow
</div>

<h1>Pipeline Workflow</h1>

<p>
La pipeline Clinical Twin implementa un workflow automatizzato di analisi
radiomica su risonanze magnetiche cerebrali T1-weighted finalizzato alla
diagnosi differenziale delle varianti di Frontotemporal Dementia (FTD).
</p>

<p>
L’intero processo è orchestrato dal microservizio <b>orchestrator</b> ed
eseguito tramite <b>Nextflow</b> all’interno del servizio
<b>nextflow_worker</b>.
</p>


<h2>Panoramica della pipeline</h2>

<div class="service-box">

<div class="codeblock">
MRI → Preprocessing → Segmentazione → Estrazione ROI → Radiomics → Inferenza KNN → Embedding UMAP → Dashboard
</div>

</div>


<h2>1. Upload della MRI</h2>

<div class="service-box">

<p>Formati supportati:</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
Il file viene salvato nel volume condiviso del sistema e registrato come task asincrono.
</p>

</div>


<h2>2. Preprocessing volumetrico</h2>

<div class="service-box">

<ul>
<li>normalizzazione dell’intensità</li>
<li>ricampionamento volumetrico</li>
<li>allineamento spaziale</li>
<li>verifica integrità del volume MRI</li>
</ul>

</div>


<h2>3. Segmentazione anatomica</h2>

<div class="service-box">

<p>Strumenti utilizzati:</p>

<ul>
<li>FreeSurfer (modalità CPU)</li>
<li>FastSurfer (modalità GPU opzionale)</li>
</ul>

<p>
Output: parcellizzazione anatomica standardizzata delle ROI cerebrali.
</p>

</div>


<h2>4. Estrazione delle ROI cerebrali</h2>

<div class="service-box">

<p>Tabella di mapping utilizzata:</p>

<div class="codeblock">
ROI_labels.tsv
</div>

<p>
Consente l’associazione tra etichette anatomiche e volumi segmentati.
</p>

</div>


<h2>5. Estrazione feature radiomiche</h2>

<div class="service-box">

<p>Configurazione PyRadiomics:</p>

<div class="codeblock">
pyradiomics.yaml
</div>

<p>Feature estratte:</p>

<ul>
<li>first-order statistics</li>
<li>GLCM texture features</li>
<li>GLRLM features</li>
<li>GLSZM features</li>
<li>shape descriptors</li>
</ul>

</div>


<h2>6. Inferenza statistica</h2>

<div class="service-box">

<p>Servizio coinvolto: <b>inference_engine</b></p>

<ul>
<li>classificazione KNN</li>
<li>similarità con dataset clinico di riferimento</li>
<li>stima classe diagnostica</li>
</ul>

</div>


<h2>7. Proiezione nello spazio latente UMAP</h2>

<div class="service-box">

<ul>
<li>visualizzazione distribuzione pazienti</li>
<li>analisi cluster diagnostici</li>
<li>identificazione nearest neighbors clinici</li>
</ul>

</div>


<h2>8. Visualizzazione dei risultati</h2>

<div class="service-box">

<ul>
<li>segmentazione multiplanare ROI (NiiVue)</li>
<li>posizione nello spazio UMAP</li>
<li>classe diagnostica stimata</li>
<li>confidence score</li>
<li>nearest neighbors clinici</li>
</ul>

</div>


<h2>9. Interpretazione tramite assistente AI</h2>

<div class="service-box">

<p>
L’assistente AI context-aware supporta l’interpretazione clinica dei risultati
radiomici e della posizione nello spazio latente.
</p>

</div>


</div>

</body>
</html>