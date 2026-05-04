<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>MLOps – Project Structure</title>

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
This section describes the organization of the MLOps repository and the role of the main directories that compose the platform’s microservices architecture.
</p>

<p>
The separation of components into independent modules facilitates code maintenance, MRI pipeline scalability, and reproducibility of radiomic analyses.
</p>


<h2>General repository structure</h2>

<p>
The repository is organized into directories dedicated to individual microservices and computational pipeline components.
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
Manages user authentication, JWT token generation, and secure access to backend platform endpoints.
</p>

<ul>
<li>user registration</li>
<li>JWT login</li>
<li>token validation</li>
<li>REST endpoint protection</li>
</ul>

</div>


<h2>orchestrator</h2>

<div class="service-box">

<p>
Coordinates asynchronous execution of MRI analyses by creating pipeline tasks and invoking Nextflow execution through the nextflow_worker service.
</p>

<ul>
<li>asynchronous task management</li>
<li>pipeline status monitoring</li>
<li>Nextflow invocation</li>
<li>backend microservices synchronization</li>
</ul>

</div>


<h2>model_service</h2>

<div class="service-box">

<p>
Manages access to the MLflow Model Registry hosted on DagsHub and prepares the diagnostic model used during inference.
</p>

<ul>
<li>champion model download</li>
<li>model versioning</li>
<li>Model Registry integration</li>
<li>inference input preparation</li>
</ul>

</div>


<h2>llm_service</h2>

<div class="service-box">

<p>
Implements the context-aware AI assistant based on Spatial RAG to support clinical interpretation and explainability of diagnostic results.
</p>

<ul>
<li>radiomic feature interpretation</li>
<li>UMAP diagnostic cluster analysis</li>
<li>multi-turn conversational memory</li>
<li>guided clinical interaction</li>
</ul>

</div>


<h2>inference_engine</h2>

<div class="service-box">

<p>
Statistical engine implemented in R using Plumber that performs KNN classification and projection of the patient into the three-dimensional UMAP latent space.
</p>

<ul>
<li>KNN classification</li>
<li>clinical similarity computation</li>
<li>3D UMAP embedding</li>
<li>nearest neighbors identification</li>
</ul>

</div>


<h2>nextflow_worker</h2>

<div class="service-box">

<p>
Executes the structural MRI pipeline through Nextflow using dedicated containers for anatomical segmentation and radiomic feature extraction.
</p>

<ul>
<li>FreeSurfer / FastSurfer segmentation</li>
<li>brain ROI extraction</li>
<li>PyRadiomics feature extraction</li>
<li>containerized Nextflow workflow</li>
</ul>

</div>


<h2>frontend</h2>

<div class="service-box">

<p>
Clinical dashboard developed in React for managing MRI analyses and interactive visualization of diagnostic results.
</p>

<ul>
<li>MRI upload</li>
<li>multiplanar viewer (NiiVue)</li>
<li>UMAP latent space visualization</li>
<li>analysis history</li>
<li>integrated AI assistant</li>
</ul>

</div>


<h2>Directory docs</h2>

<div class="service-box">

<p>
Contains the platform’s technical documentation, including architectural diagrams, user manual, and MRI pipeline documentation.
</p>

<ul>
<li>architectural diagram</li>
<li>user manual</li>
<li>pipeline documentation</li>
</ul>

</div>


</div>

</body>
</html>