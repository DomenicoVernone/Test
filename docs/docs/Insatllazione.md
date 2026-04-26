<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Installation</title>

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
Docs » Installation
</div>

<h1>Installation</h1>

<p>
This section describes the steps required to configure the Clinical Twin runtime environment, install the required dependencies, and start the complete microservices stack.
</p>


<h2>GitHub</h2>

<div class="service-box">

<p>
The Clinical Twin source code is available on GitHub. The repository
includes all platform microservices, the Nextflow-based neuroimaging
pipeline, statistical inference models, and the clinical dashboard
for exploring the latent diagnostic space.
</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD.git
</div>

<p>Clone the repository locally:</p>

<div class="codeblock">
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
</div>

</div>


<h2>Prerequisites</h2>

<div class="service-box">

<p>
Before starting the platform, it is necessary to configure the runtime
environment by installing the required components for managing Docker
containers and executing the MRI segmentation pipeline.
</p>

<ul>
<li>Docker – execution of containerized microservices</li>
<li>Docker Compose – orchestration of the application stack</li>
<li>Git – cloning the source repository</li>
<li>NVIDIA GPU (optional) – FastSurfer acceleration</li>
<li>WSL2 + CUDA drivers (Windows) – GPU support in Docker environment</li>
<li>FreeSurfer license file – required for anatomical segmentation</li>
</ul>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>
The FreeSurfer license file is mandatory to correctly execute
the brain segmentation stage of the neuroimaging pipeline.
</p>

</div>


<h2>Environment configuration</h2>

<div class="service-box">

<p>
Clinical Twin uses dedicated <code>.env</code> files for each microservice
to configure authentication parameters, model access, inference endpoints,
and integration with external services.
</p>

<p>
Copy the provided templates and customize them before starting the stack:
</p>

<div class="codeblock">
cp .env.example .env
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp model_service/.env.example model_service/.env
cp llm_service/.env.example llm_service/.env
cp frontend/.env.example frontend/.env
</div>

</div>


<h2>Main variables</h2>

<div class="service-box">

<p>
The following variables represent the main parameters used
for authentication between microservices, access to the model registry,
and integration with the AI inference service.
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
<td>Shared key for generating and validating JWT tokens between microservices</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>llm_service</td>
<td>Access key for the LLM service used by the context-aware AI assistant</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>model_service</td>
<td>MLflow server endpoint used to retrieve registered models</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>model_service</td>
<td>Authentication token for accessing the Model Registry hosted on DagsHub</td>
</tr>

</table>

</div>


<h2>FreeSurfer license</h2>

<div class="service-box">

<p>
The brain segmentation pipeline requires the presence of the FreeSurfer
license file in the Nextflow worker directory. Without this file,
the MRI preprocessing stage cannot be executed.
</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

</div>


<h2>Build Docker images</h2>

<div class="service-box">

<p>
These commands build the Docker images required to execute
the radiomics pipeline modules, including anatomical segmentation,
volumetric preprocessing, and PyRadiomics feature extraction.
</p>

<div class="codeblock">

docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</div>

</div>


<h2>Start the stack</h2>

<div class="service-box">

<p>
Starting the Docker stack initializes all platform microservices,
including the API Gateway, orchestrator, Nextflow pipeline,
inference engine, LLM service, and frontend interface.
</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Once container startup is complete, the clinical dashboard will be
available at:
</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>Create first user</h2>

<div class="service-box">

<p>
At the first platform startup, it is necessary to register a user through
the Swagger UI exposed by the API Gateway. This enables access to the
clinical dashboard and execution of radiomic analyses.
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Execute the request:</p>

<div class="codeblock">
POST /signup
</div>

<p>
After registration, it will be possible to authenticate and use the platform
for automated MRI image analysis.
</p>

</div>


</div>

</body>
</html>