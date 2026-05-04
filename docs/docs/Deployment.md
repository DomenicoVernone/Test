<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Deployment</title>

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

<h1>MLOps Platform Deployment</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
This section describes the deployment strategies of the MLOps platform
across different operational contexts, from local testing to
dedicated server infrastructures.
</p>

<p>
The entire system is designed to run using Docker containers,
ensuring dependency isolation, portability, and reproducibility
of the execution environment.
</p>

</div>

<div class="section">
<h2>2. Architectural Context</h2>

<p>
The platform is based on a microservices architecture described
in detail in the <b>System Architecture</b> section.
</p>

<p>
In the deployment context, services are orchestrated using Docker Compose
and communicate via REST APIs and shared volumes for managing
MRI data and pipeline outputs.
</p>

</div>

<div class="section">
<h2>3. Local Deployment (Development)</h2>

<p>
Local mode is used for development, debugging, and functional testing.
</p>

<p>Compatibility:</p>

<ul>
<li>Windows (WSL2)</li>
<li>macOS</li>
<li>Linux</li>
</ul>

<p>Stack startup:</p>

<pre>
docker compose up -d --build
</pre>

<p>
This command builds the images and starts all microservices.
</p>

<p>Access:</p>

<pre>
Frontend → http://localhost:5173  
API → http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>4. Deployment on Linux Server</h2>

<p>
Recommended configuration for processing large MRI datasets.
</p>

<p>Prerequisites:</p>

<ul>
<li>Docker Engine installed</li>
<li>Docker Compose</li>
<li>Multicore CPU</li>
<li>≥16 GB RAM recommended</li>
</ul>

<p>Shared volume configuration:</p>

<pre>
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</pre>

<p>
This directory is used to share data between containers
during pipeline execution.
</p>

<p>Service startup:</p>

<pre>
docker compose up -d
</pre>

</div>

<div class="section">
<h2>5. Deployment with NVIDIA GPU</h2>

<p>
Using NVIDIA GPUs enables acceleration of anatomical segmentation
through FastSurfer, significantly reducing processing time.
</p>

<p>Prerequisites:</p>

<ul>
<li>Updated NVIDIA drivers</li>
<li>Compatible CUDA version</li>
<li>NVIDIA Container Toolkit</li>
</ul>

<p>GPU availability check:</p>

<pre>
nvidia-smi
</pre>

<p>Enable GPU in the pipeline:</p>

<pre>
params.fastsurfer_device=cuda
</pre>

<p>
This parameter enables GPU usage for segmentation processes.
</p>

</div>

<div class="section">
<h2>6. Deployment with GPU MIG (Multi-Instance GPU)</h2>

<p>
On multi-user HPC systems, it is possible to use
Multi-Instance GPU (MIG) technology to partition an NVIDIA GPU
into multiple isolated instances.
</p>

<p>
This approach allows assigning a dedicated portion of GPU
to each pipeline job, improving resource isolation and
management of concurrent workloads.
</p>

<p>
Within the radiomics pipeline, MIG can be used to:
</p>

<ul>
<li>run multiple segmentations in parallel</li>
<li>avoid interference between concurrent jobs</li>
<li>optimize GPU resource utilization</li>
</ul>

<p>
Environment variable configuration:
</p>

<pre>
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</pre>

<p>
This variable identifies the specific GPU instance assigned to the container.
</p>

<p>
On systems without GPU partitioning or in CPU-only mode,
this variable can be left empty.
</p>

</div>

<div class="section">
<h2>7. Multi-Environment Deployment</h2>

<p>
The system supports multiple environments:
</p>

<ul>
<li><b>development</b> → development and debugging</li>
<li><b>staging</b> → pre-production validation</li>
<li><b>production</b> → large-scale usage</li>
</ul>

<p>
The main differences concern:
</p>

<ul>
<li>logging configuration</li>
<li>credential management</li>
<li>hardware resource allocation</li>
</ul>

</div>

<div class="section">
<h2>8. Pipeline Image Build</h2>

<p>
Before executing the pipeline, it is necessary to build
the Docker images used by Nextflow processes.
</p>

<pre>
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</pre>

<p>
These images are dynamically invoked during pipeline execution.
</p>

</div>

<div class="section">
<h2>9. Data and Volume Management</h2>

<p>
MRI data and pipeline outputs are managed through Docker volumes
shared across services.
</p>

<ul>
<li>MRI input uploaded via frontend</li>
<li>radiomic outputs generated by the pipeline</li>
<li>intermediate processing files</li>
</ul>

<p>
This approach avoids transferring large files via APIs,
improving overall system performance.
</p>

</div>

<div class="section">
<h2>10. Scalability</h2>

<p>
The architecture allows independent scaling of services:
</p>

<ul>
<li>Nextflow pipeline parallelization</li>
<li>concurrent execution of multiple MRI analyses</li>
<li>scaling of the inference engine</li>
</ul>

<p>
The system can be extended to handle high workloads
in research or production environments.
</p>

</div>

<div class="section">
<h2>11. Logging and Monitoring</h2>

<p>
The system uses multiple logging layers:
</p>

<ul>
<li>Docker logs for microservices</li>
<li>Nextflow logs for the pipeline</li>
<li>task state managed by the orchestrator</li>
</ul>

<p>
This enables comprehensive monitoring and effective debugging.
</p>

</div>

<div class="section">
<h2>12. Security</h2>

<p>
Sensitive credentials are managed via environment variables:
</p>

<ul>
<li>SECRET_KEY</li>
<li>DAGSHUB_TOKEN</li>
<li>GROQ_API_KEY</li>
</ul>

<p>
Keys must not be included in the source code and should be
configured via .env files.
</p>

</div>

<div class="section">
<h2>13. Conclusions</h2>

<p>
Container-based deployment allows running the platform
consistently across different environments, maintaining
isolation and reproducibility.
</p>

<p>
The architecture is designed to support both local usage and
deployment on dedicated infrastructures, making the system scalable
and ready for real-world scenarios.
</p>

</div>

</div>

</body>

</html>
