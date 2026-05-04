<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Configuration</title>

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

<h1>MLOps Platform Configuration</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
The configuration of the MLOps platform is based on environment
variables distributed across microservices.
</p>

<p>
This approach separates application logic from operational parameters,
facilitating deployment across different environments
(development, staging, production).
</p>

</div>

<div class="section">
<h2>2. Configuration Files</h2>

<p>
Each microservice uses a dedicated <code>.env</code> file
to manage environment variables.
</p>

<pre>
.env
api_gateway/.env
orchestrator/.env
model_service/.env
llm_service/.env
frontend/.env
</pre>

<p>
These files must be configured before starting the system.
</p>

</div>

<div class="section">
<h2>3. Main Variables</h2>

<p>
The following variables represent the core parameters for
authentication between microservices, model access,
and integration with AI services.
</p>

<table>

<tr>
<th>Variable</th>
<th>Service</th>
<th>Description</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Shared key for generating and validating JWT tokens across microservices</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>llm_service</td>
<td>Access key for the LLM service used by the context-aware AI assistant</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>model_service</td>
<td>MLflow server endpoint for retrieving registered models</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>model_service</td>
<td>Authentication token for accessing the Model Registry hosted on DagsHub</td>
</tr>

</table>

</div>

<div class="section">
<h2>4. MLflow / Model Registry Configuration</h2>

<p>
The <b>model_service</b> uses MLflow for managing
machine learning models.
</p>

<p>
Configured variables enable:
</p>

<ul>
<li>connection to the tracking server</li>
<li>download of the champion model</li>
<li>model versioning</li>
</ul>

<p>
This integration separates the model lifecycle
from inference logic.
</p>

</div>

<div class="section">
<h2>5. AI Assistant Configuration</h2>

<p>
The <b>llm_service</b> uses an external language model
to generate clinical interpretations.
</p>

<p>
The <code>GROQ_API_KEY</code> variable enables authentication
to the LLM service and must be correctly configured
to activate the AI assistant.
</p>

</div>

<div class="section">
<h2>6. GPU Configuration (Optional)</h2>

<p>
If an NVIDIA GPU is available, it is possible to accelerate
the segmentation pipeline using FastSurfer in CUDA mode.
</p>

<pre>
params.fastsurfer_device=cuda
</pre>

<p>
On CPU-only systems, this parameter must be set to:
</p>

<pre>
params.fastsurfer_device=cpu
</pre>

</div>

<div class="section">
<h2>7. MIG GPU Configuration</h2>

<p>
On multi-user HPC systems, it is possible to use
Multi-Instance GPU (MIG) technology.
</p>

<p>
This configuration allows assigning a specific GPU instance
to each pipeline job.
</p>

<pre>
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</pre>

<p>
If MIG is not used, the variable can be left empty.
</p>

</div>

<div class="section">
<h2>8. Shared Volume Configuration</h2>

<p>
The system uses a shared directory for data exchange
between microservices.
</p>

<pre>
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</pre>

<p>
This directory contains:
</p>

<ul>
<li>MRI datasets</li>
<li>radiomic outputs</li>
<li>intermediate files</li>
</ul>

</div>

<div class="section">
<h2>9. Nextflow Pipeline Configuration</h2>

<p>
Pipeline parameters are defined in the file:
</p>

<pre>
nextflow_worker/nextflow/configs/nextflow.config
</pre>

<table>

<tr>
<th>Parameter</th>
<th>Description</th>
</tr>

<tr>
<td>maxforks</td>
<td>Maximum number of parallel processes</td>
</tr>

<tr>
<td>pyradiomics_jobs</td>
<td>Number of concurrent radiomics jobs</td>
</tr>

<tr>
<td>fastsurfer_threads</td>
<td>Number of CPU threads used</td>
</tr>

<tr>
<td>brain_segmenter</td>
<td>Segmenter selection (freesurfer / fastsurfer)</td>
</tr>

</table>

</div>

<div class="section">
<h2>10. Conclusions</h2>

<p>
The configuration of the MLOps platform provides high
operational flexibility, allowing adaptation to different
environments and hardware requirements.
</p>

<p>
The separation between configuration and application logic
simplifies deployment and ensures a more secure and scalable
infrastructure management.
</p>

</div>

</div>

</body>

</html>
