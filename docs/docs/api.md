<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – API Reference</title>

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

h3 {
    margin-top: 15px;
}

/* ===== SERVICE BLOCK ===== */

.endpoint-box {
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
Docs » API Reference
</div>

<h1>API Reference</h1>

<p>
This section describes the REST endpoints exposed by the MLOps microservices
for user authentication, MRI pipeline orchestration, diagnostic inference,
and AI-based interpretation of results.
</p>

<div class="endpoint-box">

<p>
The APIs are implemented using FastAPI (Python) and Plumber (R) and enable
integration of the platform with clinical dashboards, automated workflows,
and neuroimaging research tools. Protected endpoints require a JWT token.
</p>

</div>


<h2>api_gateway</h2>

<div class="endpoint-box">

<p>
The <b>api_gateway</b> service manages user authentication, JWT generation,
and secure access to protected endpoints.
</p>

<h3>POST /signup</h3>

<p>
Registers a new user.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>POST /login</h3>

<p>
Authenticates the user and returns a JWT token to include in subsequent requests.
</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

<h3>GET /me</h3>

<p>
Returns information about the user associated with the current JWT token.
</p>

</div>


<h2>orchestrator</h2>

<div class="endpoint-box">

<p>
The <b>orchestrator</b> microservice starts and monitors execution of the
Nextflow pipeline on MRI datasets uploaded to the shared volume.
</p>

<h3>POST /analyze</h3>

<p>
Starts a new analysis on an MRI already available in the shared Docker volume.
Requires JWT authentication.
</p>

<div class="codeblock">
{
  "filename": "subject01.nii.gz"
}
</div>

<h3>GET /task/{task_id}</h3>

<p>
Returns the processing status (queued, running, completed, failed).
</p>

<h3>GET /tasks</h3>

<p>
Returns the list of analyses started by the authenticated user.
</p>

</div>


<h2>model_service</h2>

<div class="endpoint-box">

<p>
The <b>model_service</b> retrieves diagnostic models from the MLflow registry
and manages prediction preparation using extracted radiomic features.
</p>

<h3>POST /load-model</h3>

<p>
Downloads and initializes the champion model from the MLflow/DagsHub Model Registry.
</p>

<h3>POST /predict</h3>

<p>
Receives preprocessed radiomic features and returns the diagnostic prediction
using the active model.
</p>

</div>


<h2>inference_engine</h2>

<div class="endpoint-box">

<p>
The <b>inference_engine</b> microservice (Plumber/R) performs KNN classification
and UMAP projection in the diagnostic latent space.
</p>

<h3>POST /knn</h3>

<p>
Returns the estimated diagnostic class and corresponding confidence score
based on similarity with the reference dataset.
</p>

<div class="codeblock">
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</div>

<h3>POST /umap</h3>

<p>
Computes the patient's three-dimensional coordinates in the UMAP space used
for visualization and analysis of diagnostic clusters.
</p>

</div>


<h2>llm_service</h2>

<div class="endpoint-box">

<p>
The <b>llm_service</b> provides explainability features through a Spatial-RAG–based
AI assistant.
</p>

<h3>POST /chat</h3>

<p>
Sends a textual request to the AI assistant to obtain clinical interpretations
based on radiomic features, UMAP position, and diagnostic context.
</p>

<div class="codeblock">
{
  "message": "Explain this patient's cluster position"
}
</div>

</div>


<h2>Swagger UI</h2>

<div class="endpoint-box">

<p>
The complete interactive documentation is available via Swagger UI
for each FastAPI microservice running in the stack.
</p>

<div class="codeblock">
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
</div>

<p>
Swagger allows testing endpoints, inspecting JSON request/response structures,
and monitoring service behavior during development and debugging.
</p>

</div>


</div>

</body>
</html>