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
This guide describes the essential steps required to run the first MRI analysis with Clinical Twin after completing the installation and environment configuration phases.
</p>

<div class="service-box">

<p>
The workflow includes starting the microservices, creating the first user,
uploading the MRI, and automatically executing the segmentation pipeline,
radiomic feature extraction, and diagnostic inference.
</p>

</div>


<h2>1. Start the Docker stack</h2>

<div class="service-box">

<p>
Start the entire architecture using Docker Compose. The command initializes
the API Gateway, orchestrator, Nextflow pipeline, inference engine, LLM service,
and clinical dashboard.
</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Wait until all containers are active before proceeding.
</p>

</div>


<h2>2. Access the dashboard</h2>

<div class="service-box">

<p>
Once the services are running, the React dashboard is available through the browser.
The interface allows MRI upload, visualization of the UMAP diagnostic space,
and interaction with the AI assistant.
</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>3. Create the first user</h2>

<div class="service-box">

<p>
At first startup it is necessary to register a user through Swagger UI exposed
by the API Gateway. This step enables authenticated access to the dashboard.
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Execute the request:</p>

<div class="codeblock">
POST /signup
</div>

<p>
After registration it will be possible to log in and start MRI analyses.
</p>

</div>


<h2>4. Upload an MRI scan</h2>

<div class="service-box">

<p>
After login it is possible to upload a structural T1-weighted brain MRI
to automatically start the analysis pipeline.
</p>

<ul>
<li>open the upload section</li>
<li>select a .nii or .nii.gz file</li>
<li>confirm processing</li>
</ul>

<p>
The dataset is stored in the shared Docker volume and registered as an
asynchronous task managed by the orchestrator.
</p>

</div>


<h2>5. Pipeline execution</h2>

<div class="service-box">

<p>
After upload, the pipeline runs automatically through Nextflow
in the nextflow_worker service.
</p>

<p>Main processing stages include:</p>

<ul>
<li>volumetric MRI preprocessing</li>
<li>anatomical segmentation (FreeSurfer or FastSurfer)</li>
<li>brain ROI extraction</li>
<li>radiomic feature extraction with PyRadiomics</li>
<li>KNN classification</li>
<li>projection into the UMAP latent space</li>
</ul>

</div>


<h2>6. View results</h2>

<div class="service-box">

<p>
Once processing is complete, results are available in the clinical
dashboard for interactive patient case analysis.
</p>

<ul>
<li>multiplanar ROI segmentation (NiiVue viewer)</li>
<li>patient position in the UMAP latent space</li>
<li>estimated diagnostic class</li>
<li>classifier confidence score</li>
<li>clinically similar nearest neighbors</li>
</ul>

</div>


<h2>7. Query the AI assistant</h2>

<div class="service-box">

<p>
The context-aware AI assistant supports interpretation of radiomic results
by combining extracted features, position in the UMAP space,
and clinical context through a Spatial-RAG approach.
</p>

<ul>
<li>interpretation of relevant radiomic features</li>
<li>analysis of position within diagnostic clusters</li>
<li>support for clinical interpretation of predictive results</li>
</ul>

<p>
This module improves model interpretability and facilitates
evaluation of the patient case.
</p>

</div>


</div>

</body>

</html>