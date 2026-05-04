<!DOCTYPE html>

<html lang="it">
<head>
<meta charset="UTF-8">
<title>MLOps – Components & Project Structure</title>

<style>
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 40px;
    background-color: #f9f9f9;
    color: #333;
}

h1, h2, h3 {
    color: #2c3e50;
}

h1 {
    border-bottom: 2px solid #ccc;
    padding-bottom: 10px;
}

pre {
    background-color: #eee;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

.section {
    margin-bottom: 40px;
}

.box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

ul {
    margin-left: 20px;
}

/* ===== TABLE STYLE UNIFICATO ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
    font-size: 14px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
}

th {
    background-color: #2c3e50;
    color: white;
    text-align: left;
    padding: 12px;
    font-weight: 600;
}

td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

tr:hover {
    background-color: #eef2f5;
}
</style>

</head>

<body>

<div class="box">

<h1>System Components & Project Structure</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
The MLOps platform is organized as a distributed system composed of
independent microservices, each responsible for a specific stage of the
radiomics workflow.
</p>

<p>
The project structure reflects this architectural design, enabling
modularity, scalability, and clear separation of responsibilities
between components.
</p>

</div>

<div class="section">
<h2>2. Repository Structure</h2>

<p>
The repository is organized into multiple directories, each corresponding
to a microservice or core system component:
</p>

<pre>
Tesi-FTD/
├── api_gateway/
├── orchestrator/
├── model_service/
├── llm_service/
├── inference_engine/
├── nextflow_worker/
└── frontend/
</pre>

<p>
Each directory contains the source code, configuration files, and Docker
setup required for the execution of the corresponding service.
</p>

</div>

<div class="section">
<h2>3. Microservices Overview</h2>

<table>
<tr>
<th>Service</th>
<th>Role</th>
<th>Technology</th>
</tr>

<tr>
<td>api_gateway</td>
<td>Authentication, authorization, and request routing</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Workflow management and pipeline coordination</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Execution of MRI preprocessing and radiomics pipeline</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Diagnostic inference and UMAP embedding</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>model_service</td>
<td>Model registry and versioning</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>llm_service</td>
<td>AI-based explainability and clinical interpretation</td>
<td>FastAPI, LLM API</td>
</tr>

<tr>
<td>frontend</td>
<td>User interface and clinical visualization</td>
<td>React</td>
</tr>

</table>

</div>

<div class="section">
<h2>4. Service Description</h2>

<h3>api_gateway</h3>
<p>
Acts as the entry point of the platform. It handles authentication using JWT
tokens and routes incoming requests to the appropriate internal services.
</p>

<h3>orchestrator</h3>
<p>
Coordinates the execution of MRI analyses. It manages task states
(pending, running, completed, failed) and triggers the radiomics pipeline.
</p>

<h3>nextflow_worker</h3>
<p>
Executes the neuroimaging pipeline using Nextflow. It processes MRI data,
performs segmentation, extracts radiomic features, and generates structured outputs.
</p>

<h3>inference_engine</h3>
<p>
Performs diagnostic inference using machine learning models.
It applies KNN classification and projects data into a latent space using UMAP.
</p>

<h3>model_service</h3>
<p>
Handles model lifecycle management through MLflow, including model retrieval,
versioning, and integration with external registries such as DagsHub.
</p>

<h3>llm_service</h3>
<p>
Provides explainability through AI models. It generates contextual clinical
interpretations based on radiomic features and inference results.
</p>

<h3>frontend</h3>
<p>
Implements the user interface using React. It allows MRI upload,
pipeline monitoring, and visualization of diagnostic results.
</p>

</div>

<div class="section">
<h2>5. Service Communication</h2>

<p>
Microservices communicate through a hybrid approach:
</p>

<ul>
<li>REST APIs (HTTP/JSON) for control and orchestration</li>
<li>shared Docker volumes for MRI data and pipeline outputs</li>
</ul>

<p>
This design enables efficient handling of large imaging files while
maintaining interoperability between heterogeneous services.
</p>

</div>

<div class="section">
<h2>6. End-to-End Flow</h2>

<p>
The interaction between components follows a structured workflow:
</p>

<pre>
Frontend
   ↓
API Gateway
   ↓
Orchestrator
   ↓
Nextflow Worker
   ↓
Radiomics Features (CSV)
   ↓
Inference Engine
   ↓
LLM Service
   ↓
Frontend
</pre>

<p>
Each component operates independently while contributing to a
cohesive and reproducible analysis pipeline.
</p>

</div>

<div class="section">
<h2>7. Design Considerations</h2>

<ul>
<li>Microservices → modularity and independent scaling</li>
<li>Docker → reproducibility and dependency isolation</li>
<li>Nextflow → deterministic scientific workflows</li>
<li>Separation of concerns → clear system boundaries</li>
</ul>

<p>
These design choices ensure that the system remains maintainable,
extensible, and suitable for both research and production environments.
</p>

</div>

</div>

</body>
</html>
