<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Quickstart</title>

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

<h1>Quickstart – MLOps Platform Quick Start</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
This guide describes the essential steps to perform the first MRI analysis
using the MLOps platform.
</p>

<p>
The workflow includes starting the microservices, initial configuration,
and executing the full radiomics pipeline up to the visualization
of diagnostic results.
</p>

</div>

<div class="section">
<h2>2. Starting the Stack</h2>

<p>
After completing installation and configuration, start
the entire system using Docker Compose:
</p>

<pre>
docker compose up -d --build
</pre>

<p>
Wait until all containers are running.
</p>

</div>

<div class="section">
<h2>3. Accessing the Platform</h2>

<p>
Once the stack is running, the dashboard is available at:
</p>

<pre>
http://localhost:5173
</pre>

<p>
APIs are accessible via Swagger UI:
</p>

<pre>
http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>4. Creating the First User</h2>

<p>
At first startup, it is necessary to register a user via the API Gateway.
</p>

<pre>
POST /signup
</pre>

<p>
After registration, it is possible to log in and access
the platform features.
</p>

</div>

<div class="section">
<h2>5. MRI Upload</h2>

<p>
After login, it is possible to upload an MRI
in the following formats:
</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
The file is stored in the shared volume and registered
as an asynchronous task.
</p>

</div>

<div class="section">
<h2>6. Pipeline Execution</h2>

<p>
After upload, the pipeline is automatically started
by the orchestrator service.
</p>

<p>Main steps:</p>

<ul>
<li>anatomical segmentation</li>
<li>ROI extraction</li>
<li>radiomic feature extraction</li>
<li>diagnostic inference</li>
<li>UMAP projection</li>
</ul>

<p>
The pipeline status can be monitored via the dashboard.
</p>

</div>

<div class="section">
<h2>7. Results Visualization</h2>

<p>
Once processing is completed, results are available in the dashboard.
</p>

<ul>
<li>MRI segmentation (multiplanar viewer)</li>
<li>diagnostic class</li>
<li>confidence score</li>
<li>position in UMAP space</li>
<li>nearest neighbors</li>
</ul>

</div>

<div class="section">
<h2>8. AI Assistant Interaction</h2>

<p>
The AI assistant allows obtaining clinical explanations
of the results.
</p>

<p>
It is possible to:
</p>

<ul>
<li>interpret radiomic features</li>
<li>analyze position within the diagnostic cluster</li>
<li>request contextual explanations</li>
</ul>

</div>

<div class="section">
<h2>9. Complete Workflow</h2>

<pre>
Login
   ↓
Upload MRI
   ↓
Radiomics pipeline
   ↓
KNN inference
   ↓
UMAP embedding
   ↓
Dashboard visualization
   ↓
AI explainability
</pre>

<p>
This flow represents the complete analysis cycle
supported by the platform.
</p>

</div>

<div class="section">
<h2>10. Conclusions</h2>

<p>
The Quickstart allows rapid execution of a complete
radiomics pipeline without advanced configuration.
</p>

<p>
For more advanced use cases (scalability, GPU, multi-environment
configuration), refer to the Deployment and Configuration sections.
</p>

</div>

</div>

</body>

</html>
