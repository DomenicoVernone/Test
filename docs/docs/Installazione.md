<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Installation</title>

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

<h1>MLOps Platform Installation</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
This section describes the steps required to configure
the execution environment of the MLOps platform and start
the complete microservices stack.
</p>

<p>
The installation is designed to be simple and reproducible,
based on Docker containers and dedicated configuration files
for each service.
</p>

</div>

<div class="section">
<h2>2. Repository</h2>

<p>
The platform source code is available on GitHub
and includes all microservices, the Nextflow pipeline,
and the frontend dashboard.
</p>

<pre>
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
</pre>

<p>
The repository contains:
</p>

<ul>
<li>backend microservices</li>
<li>Nextflow radiomics pipeline</li>
<li>React frontend</li>
<li>Docker configuration files</li>
</ul>

</div>

<div class="section">
<h2>3. Prerequisites</h2>

<p>
Before installation, the following components are required:
</p>

<ul>
<li>Docker</li>
<li>Docker Compose</li>
<li>Git</li>
</ul>

<p>
Optional components:
</p>

<ul>
<li>NVIDIA GPU (for FastSurfer acceleration)</li>
<li>CUDA + NVIDIA Container Toolkit</li>
</ul>

<p>
It is also necessary to download the FreeSurfer license:
</p>

<pre>
https://surfer.nmr.mgh.harvard.edu/registration.html
</pre>

</div>

<div class="section">
<h2>4. Environment Configuration</h2>

<p>
The platform uses <code>.env</code> files to configure
microservice parameters.
</p>

<p>
Copy the example files:
</p>

<pre>
cp .env.example .env
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp model_service/.env.example model_service/.env
cp llm_service/.env.example llm_service/.env
cp frontend/.env.example frontend/.env
</pre>

<p>
Then configure the main environment variables used
for communication between microservices and integration with external services:
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
<h2>5. FreeSurfer License</h2>

<p>
The segmentation pipeline requires a valid FreeSurfer license.
</p>

<p>
After downloading the file:
</p>

<pre>
cp /path/to/license.txt nextflow_worker/license.txt
</pre>

<p>
Without this file, the pipeline cannot be executed.
</p>

</div>

<div class="section">
<h2>6. Docker Image Build</h2>

<p>
It is necessary to build the images used by the radiomics pipeline.
</p>

<pre>
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</pre>

<p>
These images will be automatically used by Nextflow.
</p>

</div>

<div class="section">
<h2>7. Stack Startup</h2>

<p>
Once the configuration is complete, the entire system can be started.
</p>

<pre>
docker compose up -d --build
</pre>

<p>
This command initializes:
</p>

<ul>
<li>API Gateway</li>
<li>Orchestrator</li>
<li>Nextflow Worker</li>
<li>Inference Engine</li>
<li>LLM Service</li>
<li>Frontend</li>
</ul>

</div>

<div class="section">
<h2>8. Installation Verification</h2>

<p>
After startup, verify:
</p>

<ul>
<li>running containers (docker ps)</li>
<li>absence of errors in logs</li>
<li>frontend accessibility</li>
</ul>

<p>Service access:</p>

<pre>
Frontend → http://localhost:5173
Swagger → http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>9. First User Creation</h2>

<p>
On first startup, it is necessary to create a user via the API Gateway.
</p>

<pre>
POST /signup
</pre>

<p>
After registration, it will be possible to access the platform
and start MRI analyses.
</p>

</div>

<div class="section">
<h2>10. First Analysis Execution</h2>

<p>
Once logged in:
</p>

<ul>
<li>upload an MRI (.nii or .nii.gz)</li>
<li>start the pipeline</li>
<li>monitor the status via the dashboard</li>
</ul>

<p>
The system will automatically perform:
</p>

<ul>
<li>segmentation</li>
<li>radiomic extraction</li>
<li>inference</li>
<li>result visualization</li>
</ul>

</div>

<div class="section">
<h2>11. Conclusions</h2>

<p>
The MLOps platform installation is designed to be
fast and reproducible thanks to Docker and centralized
configurations.
</p>

<p>
Once completed, the system is ready to execute full
radiomics pipelines and support clinical analysis workflows.
</p>

</div>

</div>

</body>

</html>
