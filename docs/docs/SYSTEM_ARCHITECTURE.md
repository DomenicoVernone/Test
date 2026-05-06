<!DOCTYPE html>

<html lang="en">

<head>
<meta charset="UTF-8">
<title>MLOps – System Architecture</title>

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

<h1>System Architecture</h1>

<div class="section">
<h2>1. Overview</h2>

<p>
The MLOps platform is designed as a distributed system based on
containerized microservices orchestrated through Docker Compose.
The architecture clearly separates responsibilities between data
preprocessing, workflow orchestration, statistical inference,
and clinical visualization.
</p>

<p>
This architectural approach enables:
</p>

<ul>
<li>independent component scalability</li>
<li>software dependency isolation</li>
<li>fault isolation between services</li>
<li>reproducibility of radiomics analyses</li>
<li>ease of extension and maintenance</li>
</ul>

</div>

<div class="section">
<h2>2. Distributed Architecture</h2>

<p>
The system is composed of independent containerized services
communicating through REST APIs and shared Docker volumes.
Each microservice implements a specific responsibility
within the MLOps workflow.
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
Inference Engine
  ↓
LLM Service
  ↓
Frontend
</pre>

<p>
The separation of components allows services to be updated,
deployed, and scaled independently without impacting
the entire platform.
</p>

</div>

<div class="section">
<h2>3. End-to-End Data Flow</h2>

<p>
The platform implements a sequential workflow for
radiomics analysis of MRI images.
</p>

<pre>
MRI Upload
   ↓
JWT Authentication
   ↓
Task Creation
   ↓
Nextflow Pipeline
   ↓
Radiomics Feature Extraction
   ↓
Diagnostic Inference
   ↓
UMAP Embedding
   ↓
AI Explainability
   ↓
Clinical Visualization
</pre>

<p>
Each phase generates structured outputs that are consumed
by the following service, ensuring modularity and traceability
throughout the workflow.
</p>

</div>

<div class="section">
<h2>4. Microservices Architecture</h2>

<table>

<tr>
<th>Service</th>
<th>Architectural Responsibility</th>
<th>Technology</th>
</tr>

<tr>
<td>api_gateway</td>
<td>Security layer and centralized routing</td>
<td>FastAPI, JWT</td>
</tr>

<tr>
<td>orchestrator</td>
<td>Workflow coordination and task management</td>
<td>FastAPI</td>
</tr>

<tr>
<td>nextflow_worker</td>
<td>Distributed radiomics pipeline execution</td>
<td>Nextflow, Docker</td>
</tr>

<tr>
<td>inference_engine</td>
<td>Machine learning inference and latent space embedding</td>
<td>R, Plumber</td>
</tr>

<tr>
<td>model_service</td>
<td>Model registry and version management</td>
<td>FastAPI, MLflow</td>
</tr>

<tr>
<td>llm_service</td>
<td>AI explainability and clinical interpretation</td>
<td>FastAPI, LLM API</td>
</tr>

<tr>
<td>frontend</td>
<td>Clinical interface and visualization</td>
<td>React</td>
</tr>

</table>

</div>

<div class="section">
<h2>5. Inter-Service Communication</h2>

<p>
The platform adopts a hybrid communication approach:
</p>

<ul>
<li>REST APIs (HTTP/JSON) for orchestration and control</li>
<li>shared Docker volumes for MRI files and pipeline outputs</li>
</ul>

<p>
This model reduces the overhead associated with transferring
large imaging files and improves interoperability between
heterogeneous services.
</p>

</div>

<div class="section">
<h2>6. State Management</h2>

<p>
The orchestrator maintains the task lifecycle using
a centralized state management approach.
</p>

<pre>
pending → running → completed / failed
</pre>

<p>
This mechanism enables monitoring, asynchronous execution,
and fault recovery during MRI pipeline processing.
</p>

</div>

<div class="section">
<h2>7. Architectural Principles</h2>

<ul>
<li>microservices → modularity and isolation</li>
<li>Docker → portability and environment consistency</li>
<li>Nextflow → scientific reproducibility</li>
<li>MLflow → model traceability</li>
<li>REST APIs → interoperability between services</li>
<li>model/inference separation → architectural flexibility</li>
</ul>

</div>

<div class="section">
<h2>8. Scalability and Deployment</h2>

<p>
The architecture is designed to support both research
environments and production-grade deployments.
</p>

<ul>
<li>independent microservice scaling</li>
<li>parallel execution of Nextflow pipelines</li>
<li>support for HPC environments</li>
<li>full containerization of all components</li>
<li>distributed deployment through Docker Compose</li>
</ul>

</div>

<div class="section">
<h2>9. Architectural Benefits</h2>

<ul>
<li>high system modularity</li>
<li>improved maintainability</li>
<li>simplified service testing</li>
<li>reduced coupling between components</li>
<li>reproducibility of clinical analyses</li>
<li>easy integration of new AI models</li>
</ul>

</div>

</div>

</body>

</html>