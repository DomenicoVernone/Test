<!DOCTYPE html>

<html lang="en">

<head>
<meta charset="UTF-8">
<title>MLOps – System Components and Project Structure</title>

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

/* ===== UNIFIED TABLE STYLE ===== */

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

<h1>System Components and Project Structure</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
The MLOps platform is organized as a distributed system composed
of independent microservices, each responsible for a specific
phase of the radiomics workflow.
</p>

<p>
The project structure reflects this architecture, enabling:
</p>

<ul>
<li>component modularity</li>
<li>separation of responsibilities</li>
<li>code maintainability</li>
<li>independent service scalability</li>
<li>platform extensibility</li>
</ul>

</div>

<div class="section">
<h2>2. Repository Structure</h2>

<p>
The repository is organized into separate directories, each associated
with a microservice or a core platform component.
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
Each directory contains the source code, configuration files,
and Docker definitions required to execute the corresponding service.
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
<td>Authentication, authorization and request routing</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Workflow management and pipeline coordination</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Execution of MRI and radiomics pipelines</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Diagnostic inference and UMAP embedding</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>model_service</td>
<td>Model lifecycle and version management</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>llm_service</td>
<td>AI explainability and clinical interpretation</td>
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
Represents the entry point of the platform.
It handles JWT-based authentication and routes requests
to internal services.
</p>

<h3>orchestrator</h3>
<p>
Coordinates MRI analysis execution and manages the radiomics
workflow pipeline. It maintains task states and supervises
communication between services.
</p>

<h3>nextflow_worker</h3>
<p>
Executes the neuroimaging pipeline using Nextflow.
Processes MRI data, performs segmentation, extracts radiomics
features, and generates structured outputs.
</p>

<h3>inference_engine</h3>
<p>
Performs diagnostic inference using machine learning models.
Applies KNN classification and latent space projection through UMAP.
</p>

<h3>model_service</h3>
<p>
Manages the model lifecycle using MLflow, including model retrieval,
versioning, and integration with external registries such as DagsHub.
</p>

<h3>llm_service</h3>
<p>
Provides explainability through AI models by generating contextualized
clinical interpretations based on radiomics features
and inference results.
</p>

<h3>frontend</h3>
<p>
Implements the React-based user interface, allowing MRI uploads,
pipeline monitoring, and diagnostic result visualization.
</p>

</div>

<div class="section">
<h2>5. Inter-Service Communication</h2>

<p>
The microservices communicate using a hybrid approach:
</p>

<ul>
<li>REST APIs (HTTP/JSON) for control and orchestration</li>
<li>shared Docker volumes for MRI data and pipeline outputs</li>
</ul>

<p>
This architecture enables efficient handling of large files
while ensuring interoperability between heterogeneous services.
</p>

</div>

<div class="section">
<h2>6. Operational Workflow</h2>

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
Each component operates independently while contributing
to a coherent, modular, and reproducible analysis pipeline.
</p>

</div>

<div class="section">
<h2>7. Design Choices</h2>

<ul>
<li>microservices → modularity and independent scalability</li>
<li>Docker → isolation and reproducibility</li>
<li>Nextflow → deterministic scientific workflows</li>
<li>separation of responsibilities → improved maintainability</li>
<li>independent services → fault isolation</li>
</ul>

<p>
These design choices ensure that the system is extensible,
robust, and suitable for both research environments
and production scenarios.
</p>

</div>

</div>

</body>

</html>