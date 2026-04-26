<!DOCTYPE html>
<html lang="it">

<head>
<meta charset="UTF-8">
<title>Clinical Twin – Microservices Overview</title>

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
}

</style>
</head>

<body>

<div class="content">

<div class="breadcrumb">
Docs » Microservices Overview
</div>

<h1>Microservices Overview</h1>


<p>
Clinical Twin adopts a containerized microservices architecture orchestrated through Docker Compose. Each service implements an independent functional component and communicates with the others through internal REST APIs.
</p>


<h2>Stack overview</h2>

<p>
The following diagram represents the logical sequence of services involved during MRI processing, from user management to visualization of diagnostic results.
</p>

<div class="codeblock">
api_gateway → orchestrator → nextflow_worker → model_service → inference_engine → frontend
                                     ↓
                               llm_service
</div>


<div class="service-box">

<h2>api_gateway</h2>

<p>
The api_gateway service manages user authentication, JWT-based authorization, and secure access to platform endpoints. It represents the main entry point for all client requests.
</p>

<ul>
<li>user registration</li>
<li>authenticated login</li>
<li>JWT token generation and validation</li>
<li>routing to backend microservices</li>
</ul>

</div>


<div class="service-box">

<h2>orchestrator</h2>

<p>
The orchestrator microservice coordinates asynchronous execution of MRI analyses by managing task creation and invoking the Nextflow pipeline within the nextflow_worker service.
</p>

<ul>
<li>MRI analysis task creation</li>
<li>pipeline status monitoring</li>
<li>asynchronous workflow management</li>
<li>error propagation between services</li>
</ul>

</div>


<div class="service-box">

<h2>nextflow_worker</h2>

<p>
The nextflow_worker service executes the structural MRI pipeline using Nextflow and dedicated containers for anatomical segmentation and radiomic feature extraction.
</p>

<ul>
<li>volumetric MRI preprocessing</li>
<li>FreeSurfer or FastSurfer segmentation</li>
<li>brain region (ROI) extraction</li>
<li>PyRadiomics feature computation</li>
</ul>

</div>


<div class="service-box">

<h2>model_service</h2>

<p>
The model_service manages access to the MLflow Model Registry hosted on DagsHub and prepares the diagnostic model used during inference.
</p>

<ul>
<li>champion model download</li>
<li>model versioning</li>
<li>MLflow integration</li>
<li>inference input preparation</li>
</ul>

</div>


<div class="service-box">

<h2>inference_engine</h2>

<p>
Implemented in R using Plumber, the inference_engine service performs KNN classification on radiomic features and computes the patient's position in the three-dimensional UMAP latent space.
</p>

<ul>
<li>diagnostic class estimation</li>
<li>clinical similarity computation</li>
<li>3D UMAP embedding</li>
<li>nearest neighbors identification</li>
</ul>

</div>


<div class="service-box">

<h2>llm_service</h2>

<p>
The llm_service provides assisted clinical interpretation through a Spatial-RAG approach, integrating radiomic features, UMAP coordinates, and conversational context.
</p>

<ul>
<li>radiomic feature interpretation</li>
<li>UMAP diagnostic cluster analysis</li>
<li>model explainability support</li>
<li>Groq API integration</li>
</ul>

</div>


<div class="service-box">

<h2>frontend</h2>

<p>
The React dashboard represents the platform’s clinical interface and allows management of MRI analyses and interactive exploration of diagnostic results.
</p>

<ul>
<li>MRI upload</li>
<li>NiiVue multiplanar viewer</li>
<li>UMAP latent space visualization</li>
<li>analysis history</li>
<li>integrated AI assistant</li>
</ul>

</div>

</div>

</body>

</html>