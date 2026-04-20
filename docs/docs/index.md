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

/* ===== MAIN CONTENT ===== */

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

/* ===== LIST ===== */

ul {
    margin-top: 10px;
}

/* ===== NAVIGATION BUTTONS ===== */

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

<!-- ===== SIDEBAR ===== -->


<!-- ===== MAIN CONTENT ===== -->

<div class="content">

<div class="breadcrumb">
Docs » Introduction
</div>

<h1>Introduction</h1>


<h2>Description</h2>

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


<h2>Features</h2>

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


<h2>Source Code</h2>

<p>The source code is currently hosted on GitHub at:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD
</div>


<h2>Add the FreeSurfer license</h2>


<p>
FreeSurfer requires a valid license file to execute the segmentation pipeline.
Download the license from:
</p>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>
After downloading the file, copy it into the Nextflow worker directory:
</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

<p>
Without this file, the segmentation stage of the neuroimaging pipeline cannot start.
</p>
<h2>Contributions</h2>

<p>
Clinical Twin is currently maintained as part of an academic research
project. Suggestions, improvements, and collaborations related to
radiomics workflows, neuroimaging pipelines, or explainable AI in
clinical environments are welcome.
</p>

<p>
For issues or feature requests, refer to the repository:
</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD/issues
</div>


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