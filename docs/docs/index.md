<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Introduzione</title>

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

/* ===== SERVICE BOX ===== */

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

/* ===== LIST ===== */

ul {
    margin-top: 10px;
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
Docs » Introduzione
</div>

<h1>Introduzione</h1>


<h2>Descrizione</h2>

<div class="service-box">

<p>
Clinical Twin è una piattaforma di supporto alle decisioni cliniche progettata
per la diagnosi differenziale delle varianti di Demenza Frontotemporale (FTD)
attraverso l’analisi radiomica di risonanze magnetiche cerebrali strutturali.
</p>

<p>
Il sistema integra una pipeline automatizzata di neuroimaging basata su
FreeSurfer / FastSurfer e PyRadiomics, un motore di inferenza statistica
implementato in R, un assistente AI context-aware basato su Spatial RAG
e una dashboard interattiva sviluppata in React per la visualizzazione
multiplanare delle immagini e l’esplorazione dello spazio diagnostico latente
generato tramite UMAP.
</p>

</div>


<h2>Funzionalità principali</h2>

<div class="service-box">

<ul>
<li>Segmentazione automatica MRI tramite FreeSurfer o FastSurfer</li>
<li>Estrazione di feature radiomiche con PyRadiomics</li>
<li>Motore di inferenza statistica basato su KNN implementato in R</li>
<li>Proiezione nello spazio latente 3D tramite UMAP</li>
<li>Assistente clinico Spatial RAG per supporto all’interpretabilità</li>
<li>Viewer MRI multiplanare interattivo (integrazione NiiVue)</li>
<li>Architettura a microservizi orchestrata con Docker Compose</li>
<li>Versionamento e tracciamento modelli tramite MLflow e DagsHub</li>
</ul>

</div>


<h2>Codice sorgente</h2>

<div class="service-box">

<p>Repository GitHub:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD
</div>

</div>


<h2>Aggiunta della licenza FreeSurfer</h2>

<div class="service-box">

<p>
FreeSurfer richiede un file di licenza valido per eseguire la pipeline di
segmentazione neuroimaging. Scaricare la licenza da:
</p>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>Dopo il download eseguire:</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

<p>
Senza questo file la pipeline di segmentazione non può essere avviata.
</p>

</div>


<h2>Contributi</h2>

<div class="service-box">

<p>
Clinical Twin è attualmente sviluppato come progetto accademico di ricerca.
Sono benvenuti contributi relativi a:
</p>

<ul>
<li>workflow radiomici</li>
<li>pipeline di neuroimaging</li>
<li>explainable AI in ambito clinico</li>
</ul>

<p>Segnalazione issue:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD/issues
</div>

</div>


</div>

</body>
</html>