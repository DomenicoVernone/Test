<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Deployment</title>

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
Docs » Deployment
</div>

<h1>Deployment</h1>

<p>
This section describes the deployment modes of the Clinical Twin platform in local environments, research servers, and dedicated GPU infrastructures.
</p>

<div class="service-box">

<p>
Clinical Twin can be executed both on local workstations for development and testing,
and on dedicated Linux servers for processing large-scale MRI datasets.
The containerized architecture based on Docker Compose ensures portability,
reproducibility, and isolation of microservices.
</p>

</div>


<h2>Local deployment (Docker Desktop)</h2>

<div class="service-box">

<p>
Recommended configuration for development, functional validation, and testing on single MRI datasets.
</p>

<p>Compatible with:</p>

<ul>
<li>Windows (WSL2)</li>
<li>macOS</li>
<li>Linux</li>
</ul>

<p>Start the application stack:</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
This command initializes the API Gateway, orchestrator, Nextflow worker,
inference engine, LLM service, and React dashboard.
</p>

<p>Access the dashboard:</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>Deployment on Linux server</h2>

<div class="service-box">

<p>
Recommended configuration for laboratory environments or departmental servers
dedicated to automated MRI dataset processing.
</p>

<p>Prerequisites:</p>

<ul>
<li>Docker Engine installed</li>
<li>Docker Compose</li>
<li>multicore CPU</li>
<li>≥16 GB RAM recommended</li>
</ul>

<p>
On Linux bare-metal systems it is necessary to configure the shared directory
used by the Nextflow pipeline:
</p>

<div class="codeblock">
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</div>

<p>Start services:</p>

<div class="codeblock">
docker compose up -d
</div>

</div>


<h2>Deployment with NVIDIA GPU</h2>

<div class="service-box">

<p>
Using an NVIDIA GPU accelerates anatomical segmentation through FastSurfer,
significantly reducing processing time compared to CPU mode.
</p>

<p>Prerequisites:</p>

<ul>
<li>updated NVIDIA drivers</li>
<li>compatible CUDA</li>
<li>NVIDIA Container Toolkit</li>
</ul>

<p>Verify GPU availability:</p>

<div class="codeblock">
nvidia-smi
</div>

<p>
Enable GPU in the Nextflow pipeline:
</p>

<div class="codeblock">
params.fastsurfer_device=cuda
</div>

</div>


<h2>Deployment with MIG GPU (Multi-Instance GPU)</h2>

<div class="service-box">

<p>
On multi-user HPC systems it is possible to assign a specific MIG instance
to the pipeline to isolate GPU resources between concurrent jobs.
</p>

<p>Environment variable configuration:</p>

<div class="codeblock">
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</div>

<p>
Leave empty on systems without GPU partitioning.
</p>

</div>


<h2>Nextflow pipeline deployment</h2>

<div class="service-box">

<p>
Clinical Twin uses a Docker-out-of-Docker (DooD) model to allow
the nextflow_worker service to execute dedicated containers for segmentation,
MRI preprocessing, and radiomic feature extraction.
</p>

<p>
Before running the pipeline it is necessary to build the worker images:
</p>

<div class="codeblock">
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</div>

<p>
These images are automatically used by the Nextflow processes.
</p>

</div>


<h2>Production deployment (recommended)</h2>

<div class="service-box">

<p>
For analysis on large clinical datasets, a dedicated Linux server configuration
with GPU acceleration and persistent storage for MRI datasets and radiomic outputs is recommended.
</p>

<p>Suggested configuration:</p>

<ul>
<li>dedicated Linux server</li>
<li>CUDA-compatible NVIDIA GPU</li>
<li>Docker Engine</li>
<li>persistent volume for MRI datasets</li>
<li>backup system for radiomic features and models</li>
</ul>

<p>Logical service architecture:</p>

<div class="codeblock">
Frontend → API Gateway → Orchestrator → Nextflow Worker → Inference Engine → LLM Service
</div>

<p>
This configuration ensures microservice isolation,
pipeline scalability, and support for reproducible radiomics workflows.
</p>

</div>

</div>

</body>

</html>