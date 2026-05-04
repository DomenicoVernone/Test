<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – System Architecture</title>

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

/* ===== TABLE ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
}

th {
    background: #f0f0f0;
}

/* ===== IMAGE BLOCK ===== */

.arch-image {
    text-align: center;
}

.arch-image img {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}

.caption {
    font-size: 14px;
    color: gray;
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
Docs » System Architecture
</div>

<h1>System Architecture</h1>


<div class="service-box">

<p>
MLOps is designed as a modular platform based on containerized
microservices orchestrated through Docker Compose.
The architecture clearly separates neuroimaging preprocessing,
statistical inference, model management, and the clinical interface.
</p>

</div>


<h2>General overview</h2>

<div class="service-box">

<p>
The following diagram represents the logical structure of the microservices
and the data flow within the MLOps pipeline.
</p>

<div class="arch-image">
<img src="../assets/architecture.png" alt="MLOps architecture diagram">
<div class="caption">
Figure: Microservices architecture of the MLOps platform
</div>
</div>

<p>Main operational workflow:</p>

<div class="codeblock">
MRI → Segmentation → Radiomic extraction → KNN inference → UMAP embedding → Clinical dashboard
</div>

</div>


<h2>Microservices architecture</h2>

<div class="service-box">

<table>

<tr>
<th>Service</th>
<th>Technology</th>
<th>Port</th>
<th>Function</th>
</tr>

<tr>
<td>api_gateway</td>
<td>FastAPI, JWT</td>
<td>8000</td>
<td>User authentication and request routing</td>
</tr>

<tr>
<td>orchestrator</td>
<td>FastAPI</td>
<td>8001</td>
<td>Asynchronous pipeline task management</td>
</tr>

<tr>
<td>llm_service</td>
<td>FastAPI, Spatial RAG</td>
<td>8002</td>
<td>Context-aware AI assistant</td>
</tr>

<tr>
<td>model_service</td>
<td>FastAPI, MLflow</td>
<td>8003</td>
<td>Champion model management</td>
</tr>

<tr>
<td>inference_engine</td>
<td>R, Plumber</td>
<td>8004</td>
<td>KNN inference and UMAP projection</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Nextflow, FreeSurfer</td>
<td>8005</td>
<td>MRI segmentation and radiomics extraction</td>
</tr>

<tr>
<td>frontend</td>
<td>React, Plotly, NiiVue</td>
<td>5173</td>
<td>Interactive clinical dashboard</td>
</tr>

</table>

</div>


<h2>Neuroimaging pipeline</h2>

<div class="service-box">

<p>
Main stages of the preprocessing and radiomic analysis pipeline applied
to structural MRI images.
</p>

<ul>
<li>volumetric MRI preprocessing</li>
<li>FreeSurfer / FastSurfer anatomical segmentation</li>
<li>brain ROI extraction</li>
<li>PyRadiomics feature extraction</li>
</ul>

</div>


<h2>inference_engine</h2>

<div class="service-box">

<p>
Implements KNN classification and 3D UMAP projection
to represent the patient within the diagnostic latent space.
</p>

<ul>
<li>clinical nearest neighbors</li>
<li>diagnostic clusters</li>
<li>interpretable decision support</li>
</ul>

</div>


<h2>Context-aware AI assistant</h2>

<div class="service-box">

<p>
Provides interpretative support for model predictions by integrating
radiomic features, UMAP embeddings, and conversational clinical context.
</p>

<ul>
<li>radiomic feature interpretation</li>
<li>position analysis in the UMAP space</li>
<li>clinical explainability support</li>
<li>multi-turn conversational memory</li>
</ul>

</div>



</div>

</body>
</html>
