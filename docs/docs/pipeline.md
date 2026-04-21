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

<div class="service-box">

<p>
La pipeline Clinical Twin implementa un workflow automatizzato di analisi
radiomica su risonanze magnetiche strutturali T1-weighted finalizzato alla
diagnosi differenziale delle varianti della Frontotemporal Dementia (FTD).
</p>

<p>
L’esecuzione è orchestrata dal microservizio <b>orchestrator</b>, mentre
l’elaborazione computazionale viene gestita tramite <b>Nextflow</b> all’interno
del servizio <b>nextflow_worker</b>, garantendo parallelizzazione,
riproducibilità e scalabilità dell’intero processo neuroimaging.
</p>

</div>


<h2>Panoramica della pipeline</h2>

<div class="service-box">

<p>
Il flusso operativo della pipeline segue una sequenza strutturata di
trasformazioni volumetriche, estrazione di biomarcatori radiomici e
inferenza statistica nello spazio latente diagnostico.
</p>

<div class="codeblock">
MRI → Preprocessing → Segmentazione → Estrazione ROI → Radiomics → Inferenza KNN → Embedding UMAP → Dashboard
</div>

</div>


<h2>1. Upload della MRI</h2>

<div class="service-box">

<p>
L’utente carica una risonanza magnetica cerebrale strutturale tramite la
dashboard clinica. I dati vengono salvati nel volume condiviso Docker e
registrati come task asincrono gestito dall’orchestrator.
</p>

<p>Formati supportati:</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
Questa fase rappresenta il punto di ingresso della pipeline neuroimaging.
</p>

</div>


<h2>2. Preprocessing volumetrico</h2>

<div class="service-box">

<p>
Il preprocessing prepara il volume MRI per la segmentazione anatomica
standardizzata e l’estrazione delle feature radiomiche.
</p>

<ul>
<li>normalizzazione dell’intensità voxel</li>
<li>ricampionamento isotropico del volume</li>
<li>allineamento spaziale stereotassico</li>
<li>verifica integrità del dataset MRI</li>
</ul>

<p>
Queste operazioni riducono la variabilità inter-scanner e migliorano la
robustezza delle feature estratte.
</p>

</div>


<h2>3. Segmentazione anatomica</h2>

<div class="service-box">

<p>
La segmentazione cerebrale consente la parcellizzazione della corteccia
in regioni anatomiche standardizzate utilizzabili per analisi radiomiche
regionalizzate.
</p>

<p>Strumenti utilizzati:</p>

<ul>
<li>FreeSurfer (modalità CPU)</li>
<li>FastSurfer (modalità GPU opzionale)</li>
</ul>

<p>
L’output consiste in mappe di etichettatura volumetrica delle ROI corticali
e sottocorticali.
</p>

</div>


<h2>4. Estrazione delle ROI cerebrali</h2>

<div class="service-box">

<p>
Le regioni anatomiche segmentate vengono associate a etichette standard
tramite la tabella di mapping utilizzata dalla pipeline.
</p>

<div class="codeblock">
ROI_labels.tsv
</div>

<p>
Questa fase consente la costruzione di un dataset strutturato per
l’estrazione delle feature radiomiche regionali.
</p>

</div>


<h2>5. Estrazione feature radiomiche</h2>

<div class="service-box">

<p>
Le feature radiomiche vengono estratte tramite <b>PyRadiomics</b> utilizzando
una configurazione parametrica definita nel file YAML della pipeline.
</p>

<div class="codeblock">
pyradiomics.yaml
</div>

<p>Feature principali estratte:</p>

<ul>
<li>first-order intensity statistics</li>
<li>GLCM texture features</li>
<li>GLRLM texture features</li>
<li>GLSZM texture features</li>
<li>shape descriptors tridimensionali</li>
</ul>

<p>
Queste feature rappresentano biomarcatori quantitativi utilizzati per
la classificazione diagnostica.
</p>

</div>


<h2>6. Inferenza statistica</h2>

<div class="service-box">

<p>
Le feature radiomiche vengono inviate al microservizio <b>inference_engine</b>,
che esegue la classificazione diagnostica nello spazio delle feature.
</p>

<ul>
<li>classificazione tramite algoritmo K-Nearest Neighbors (KNN)</li>
<li>calcolo similarità con pazienti del dataset di riferimento</li>
<li>stima probabilistica della classe diagnostica FTD</li>
</ul>

<p>
Questa fase rappresenta il core decisionale del sistema Clinical Twin.
</p>

</div>


<h2>7. Proiezione nello spazio latente UMAP</h2>

<div class="service-box">

<p>
Le feature vengono proiettate in uno spazio latente tridimensionale tramite
UMAP per consentire l’esplorazione visiva della distribuzione dei pazienti.
</p>

<ul>
<li>visualizzazione distribuzione campioni clinici</li>
<li>identificazione cluster diagnostici</li>
<li>ricerca nearest neighbors clinicamente simili</li>
</ul>

<p>
Lo spazio UMAP costituisce la base del modello di explainability visiva.
</p>

</div>


<h2>8. Visualizzazione dei risultati</h2>

<div class="service-box">

<p>
I risultati vengono resi disponibili nella dashboard React interattiva
per supportare l’analisi clinica del caso paziente.
</p>

<ul>
<li>segmentazione multiplanare delle ROI cerebrali (NiiVue)</li>
<li>posizione del paziente nello spazio latente UMAP</li>
<li>classe diagnostica stimata</li>
<li>confidence score del classificatore</li>
<li>nearest neighbors clinicamente simili</li>
</ul>

</div>


<h2>9. Interpretazione tramite assistente AI</h2>

<div class="service-box">

<p>
L’assistente AI context-aware utilizza un approccio Spatial-RAG per
interpretare i risultati radiomici e fornire spiegazioni clinicamente
contestualizzate sulla posizione del paziente nello spazio diagnostico.
</p>

<p>
Questo modulo migliora l’interpretabilità del modello e supporta il
processo decisionale medico.
</p>

</div>



</div>

</body>
</html>