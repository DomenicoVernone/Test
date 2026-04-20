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
    display: flex;
    background: #f5f6f7;
}

/* ===== SIDEBAR ===== */

.sidebar {
    width: 300px;
    height: 100vh;
    background: linear-gradient(#2f6f95, #244f6a);
    color: white;
    position: fixed;
    padding: 20px;
    box-sizing: border-box;
}

.sidebar h2 {
    margin-top: 0;
}

.sidebar input {
    width: 100%;
    padding: 8px;
    border-radius: 6px;
    border: none;
    margin: 15px 0;
}

.sidebar ul {
    list-style: none;
    padding-left: 0;
}

.sidebar li {
    padding: 6px 0;
    opacity: 0.9;
}

.sidebar li.active {
    font-weight: bold;
    color: white;
}

/* ===== MAIN CONTENT ===== */

.content {
    margin-left: 320px;
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
    margin-top: 25px;
}

/* ===== CODE BLOCK ===== */

.codeblock {
    background: #eeeeee;
    padding: 14px;
    border-radius: 6px;
    font-family: monospace;
    margin: 15px 0;
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

/* ===== NAVIGATION BUTTONS ===== */

.nav-buttons {
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
}

.button {
    background: #e0e0e0;
    border-radius: 6px;
    padding: 10px 15px;
    text-decoration: none;
    color: black;
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

<!-- ===== SIDEBAR ===== -->

<div class="sidebar">

<h2>🏠 Clinical Twin</h2>

<input placeholder="Search docs">

<ul>
<li>Introduction</li>
<li class="active">Installation</li>
<li>Quickstart</li>
<li>User Guide</li>
</ul>

</div>


<!-- ===== MAIN CONTENT ===== -->

<div class="content">

<div class="breadcrumb">
Docs » Installation
</div>

<h1>Installation</h1>


<h2>GitHub</h2>

<p>The source code is currently hosted on GitHub at:</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD.git
</div>

<p>Clone the repository:</p>

<div class="codeblock">
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
</div>


<h2>Prerequisites</h2>

<ul>
<li>Docker</li>
<li>Docker Compose</li>
<li>Git</li>
<li>NVIDIA GPU (optional – required only for FastSurfer)</li>
<li>WSL2 + CUDA drivers (Windows GPU setup)</li>
<li>FreeSurfer license file</li>
</ul>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>


<h2>Environment configuration</h2>

<p>Copy the environment templates:</p>

<div class="codeblock">
cp .env.example .env
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp model_service/.env.example model_service/.env
cp llm_service/.env.example llm_service/.env
cp frontend/.env.example frontend/.env
</div>


<h2>Main variables</h2>

<table>

<tr>
<th>Variable</th>
<th>Service</th>
<th>Description</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Shared JWT secret</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>llm_service</td>
<td>Groq API key</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>model_service</td>
<td>DagsHub MLflow tracking server</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>model_service</td>
<td>DagsHub authentication token</td>
</tr>

</table>


<h2>FreeSurfer license</h2>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>


<h2>Build Docker images</h2>

<div class="codeblock">
docker build -t clinical-freesurfer -f nextflow_worker/freesurfer.dockerfile nextflow_worker/
docker build -t clinical-fsl -f nextflow_worker/fsl.dockerfile nextflow_worker/
docker build -t clinical-pyradiomics -f nextflow_worker/pyradiomics.dockerfile nextflow_worker/
</div>


<h2>Start the stack</h2>

<div class="codeblock">
docker compose up -d --build
</div>

<p>Frontend available at:</p>

<div class="codeblock">
http://localhost:5173
</div>


<h2>Create first user</h2>

<p>Open Swagger UI:</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Execute:</p>

<div class="codeblock">
POST /signup
</div>


<div class="nav-buttons">

<a class="button">⬅ Previous</a>
<a class="button">Next ➡</a>

</div>


<div class="footer">

© 2025 Clinical Twin Documentation  
Built with custom HTML/CSS (ReadTheDocs style)

</div>

</div>

</body>
</html>