<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Introduction</title>

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
MLOps is a clinical decision support platform designed
for the differential diagnosis of Frontotemporal Dementia (FTD) variants
through radiomic analysis of structural brain MRI scans.
</p>

<p>
The system integrates an automated neuroimaging pipeline based on
FreeSurfer / FastSurfer and PyRadiomics, a statistical inference engine
implemented in R, a context-aware AI assistant based on Spatial RAG,
and an interactive dashboard developed in React for multiplanar image
visualization and exploration of the latent diagnostic space
generated using UMAP.
</p>

</div>


<h2>Main features</h2>

<div class="service-box">

<ul>
<li>Automatic MRI segmentation using FreeSurfer or FastSurfer</li>
<li>Radiomic feature extraction with PyRadiomics</li>
<li>KNN-based statistical inference engine implemented in R</li>
<li>Projection into a 3D latent space using UMAP</li>
<li>Spatial RAG clinical assistant for interpretability support</li>
<li>Interactive multiplanar MRI viewer (NiiVue integration)</li>
<li>Microservices architecture orchestrated with Docker Compose</li>
<li>Model versioning and tracking using MLflow and DagsHub</li>
</ul>

</div>


<h2>Source code</h2>

<div class="service-box">

<p>GitHub repository:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD
</div>

</div>


<h2>Adding the FreeSurfer license</h2>

<div class="service-box">

<p>
FreeSurfer requires a valid license file to execute the neuroimaging
segmentation pipeline. Download the license from:
</p>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>After downloading, run:</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

<p>
Without this file, the segmentation pipeline cannot be started.
</p>

</div>


<h2>Contributions</h2>

<div class="service-box">

<p>
MLOps is currently developed as an academic research project.
Contributions related to the following areas are welcome:
</p>

<ul>
<li>radiomics workflows</li>
<li>neuroimaging pipelines</li>
<li>clinical explainable AI</li>
</ul>

<p>Issue reporting:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD/issues
</div>

</div>


</div>

</body>
</html>