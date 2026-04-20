<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Introduction</title>

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
Docs » Introduction
</div>

<h1>Introduction</h1>


<h2>Description</h2>

<div class="service-box">

<p>
Clinical Twin is a clinical decision-support platform designed for the
differential diagnosis of Frontotemporal Dementia (FTD) variants using
radiomic analysis of structural brain MRI scans.
</p>

<p>
The system integrates an automated neuroimaging pipeline based on
FreeSurfer / FastSurfer and PyRadiomics, a statistical inference engine
implemented in R, a context-aware AI assistant powered by Spatial RAG,
and an interactive React dashboard for multiplanar visualization and
exploration of the latent diagnostic space generated through UMAP.
</p>

</div>


<h2>Features</h2>

<div class="service-box">

<ul>
<li>Automated MRI segmentation using FreeSurfer or FastSurfer</li>
<li>Radiomic feature extraction with PyRadiomics</li>
<li>KNN-based statistical inference engine implemented in R</li>
<li>3D latent space projection using UMAP</li>
<li>Spatial RAG clinical assistant for explainability support</li>
<li>Interactive multiplanar MRI viewer (NiiVue integration)</li>
<li>Microservice architecture orchestrated with Docker Compose</li>
<li>Model versioning and tracking via MLflow and DagsHub</li>
</ul>

</div>


<h2>Source Code</h2>

<div class="service-box">

<p>Repository GitHub:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD
</div>

</div>


<h2>Add the FreeSurfer license</h2>

<div class="service-box">

<p>
FreeSurfer richiede un file di licenza valido per eseguire la pipeline di segmentazione.
Scaricare la licenza da:
</p>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>Dopo il download:</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

<p>
Senza questo file la pipeline di segmentazione non può essere avviata.
</p>

</div>


<h2>Contributions</h2>

<div class="service-box">

<p>
Clinical Twin è attualmente sviluppato come progetto accademico di ricerca.
Sono benvenuti contributi relativi a:
</p>

<ul>
<li>radiomics workflows</li>
<li>neuroimaging pipelines</li>
<li>explainable AI in clinical environments</li>
</ul>

<p>Issue tracker:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD/issues
</div>

</div>


</div>

</body>
</html>