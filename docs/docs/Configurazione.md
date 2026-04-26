<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Configuration</title>

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

/* ===== TABLE ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
}

th {
    background: #f0f0f0;
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
Docs » Configuration
</div>

<h1>Configuration</h1>

<p>
This section describes the main configuration variables used by Clinical Twin microservices to manage authentication, model access, integration with AI services, and radiomics pipeline parameters.
</p>

<div class="service-box">

<p>
Clinical Twin uses configuration files distributed across the different
platform microservices to manage authentication, orchestration of the
neuroimaging pipeline, access to registered models, and integration
with inference services based on language models.
</p>

<p>
Proper configuration of environment variables is required to ensure
communication between services and correct operation of the complete
radiomics pipeline.
</p>

</div>


<h2>Main .env files</h2>

<div class="service-box">

<p>
Each microservice uses a dedicated <code>.env</code> file containing
configuration variables specific to authentication, resource access,
and operational parameters.
</p>

<div class="codeblock">
.env
api_gateway/.env
orchestrator/.env
model_service/.env
llm_service/.env
frontend/.env
</div>

<p>
These files must be configured before starting the Docker stack.
</p>

</div>


<h2>Shared variables (JWT)</h2>

<div class="service-box">

<p>
JWT variables enable secure authentication between microservices
through digitally signed tokens and ensure protection of internal
platform requests.
</p>

<table>

<tr>
<th>Variable</th>
<th>Services</th>
<th>Description</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Shared cryptographic key for generating and validating JWT tokens between services</td>
</tr>

</table>

</div>


<h2>MLflow / DagsHub configuration</h2>

<div class="service-box">

<p>
These variables enable access to the MLflow Model Registry hosted
on DagsHub and allow automatic retrieval of the champion model
used for diagnostic inference.
</p>

<table>

<tr>
<th>Variable</th>
<th>Description</th>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>MLflow server endpoint used to track experiments and models</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_USERNAME</td>
<td>DagsHub account username for registry authentication</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>Access token for the remote Model Registry on DagsHub</td>
</tr>

<tr>
<td>REPO_OWNER</td>
<td>Username or organization that owns the MLflow repository</td>
</tr>

<tr>
<td>REPO_NAME</td>
<td>Name of the repository containing registered models</td>
</tr>

</table>

</div>


<h2>AI assistant configuration</h2>

<div class="service-box">

<p>
The context-aware clinical assistant uses external language models
via APIs. The following variable enables authentication with the
LLM service used to support interpretation of radiomic results.
</p>

<table>

<tr>
<th>Variable</th>
<th>Description</th>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>API key for accessing the language model used by the AI service</td>
</tr>

</table>

</div>


<h2>GPU configuration (optional)</h2>

<div class="service-box">

<p>
If an NVIDIA GPU is available, FastSurfer can use CUDA acceleration
to significantly reduce MRI segmentation processing time.
</p>

<div class="codeblock">
MIG_DEVICE=
</div>

<p>
On systems with partitioned GPUs (Multi-Instance GPU), it is possible
to specify the identifier of the MIG instance assigned to the container.
Leave empty on CPU-only systems or standard GPU setups.
</p>

</div>


<h2>Shared volumes configuration</h2>

<div class="service-box">

<p>
The following variable defines the host directory used to share
MRI datasets and intermediate outputs between containers in the
Nextflow pipeline.
</p>

<div class="codeblock">
HOST_SHARED_VOLUME_DIR=
</div>

<p>
This parameter is mainly required on Linux bare-metal systems.
On Docker Desktop (Windows/macOS) it may remain unset.
</p>

</div>


<h2>Nextflow pipeline configuration</h2>

<div class="service-box">

<p>
The main radiomics pipeline parameters are defined in the Nextflow
configuration file. These settings control parallelization,
segmentation mode, and the number of radiomics jobs executed simultaneously.
</p>

<div class="codeblock">
nextflow_worker/nextflow/configs/nextflow.config
</div>

<table>

<tr>
<th>Parameter</th>
<th>Description</th>
</tr>

<tr>
<td>params.maxforks</td>
<td>Maximum number of parallel processes that can run simultaneously</td>
</tr>

<tr>
<td>params.fastsurfer_threads</td>
<td>Number of CPU threads used during FastSurfer segmentation</td>
</tr>

<tr>
<td>params.fastsurfer_device</td>
<td>Execution device: cpu or cuda</td>
</tr>

<tr>
<td>params.pyradiomics_jobs</td>
<td>Maximum number of radiomics extractions executed in parallel</td>
</tr>

<tr>
<td>params.brain_segmenter</td>
<td>Segmenter selection: freesurfer or fastsurfer</td>
</tr>

</table>

</div>


</div>

</body>
</html>