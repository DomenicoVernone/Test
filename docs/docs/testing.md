<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Test Plan</title>

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
    max-width: 950px;
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
}

h2 {
    margin-top: 40px;
    font-size: 26px;
}

h3 {
    margin-top: 20px;
}

/* ===== SERVICE BLOCK ===== */

.service-box {
    background: white;
    padding: 18px;
    border-radius: 8px;
    margin-top: 15px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}

/* ===== CODE BLOCK ===== */

.codeblock {
    background: #eeeeee;
    padding: 14px;
    border-radius: 6px;
    font-family: monospace;
    margin-top: 10px;
    white-space: pre-line;
}

/* ===== TABLE ===== */

table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
}

th {
    background: #f0f0f0;
}

.note {
    margin-top: 8px;
    color: #555;
}

</style>

</head>

<body>

<div class="content">

<div class="breadcrumb">
Docs » Test Plan
</div>

<h1>Complete Test Plan – Clinical Twin</h1>

<div class="service-box">

<p>
This test plan defines the functional, structural, and performance validation procedures of the <strong>ClinicalTwin</strong> platform.
</p>

<p>
The verification activities cover the entire application stack, including:
</p>

<ul>
<li>containerized backend microservices</li>
<li>Nextflow neuroimaging pipeline</li>
<li>statistical inference engine (KNN + UMAP)</li>
<li>MLflow model registry</li>
<li>Spatial RAG LLM assistant</li>
<li>React clinical dashboard</li>
</ul>

<p class="note">
The objective of the test plan is to ensure computational correctness, operational robustness, and reproducibility of the diagnostic workflow.
</p>

</div>

<h2>1. Docker stack deployment test</h2>

<div class="service-box">

<p>
This phase verifies the correct build of container images and the startup of the entire microservices architecture.
</p>

<h3>Scientific pipeline image build</h3>

<div class="codeblock">
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/
docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/
docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</div>

<p>
Expected:
</p>

<ul>
<li>no errors during build</li>
<li>images available in the local Docker registry</li>
<li>runtime compatibility with Nextflow</li>
</ul>

<h3>Stack startup</h3>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Verification:
</p>

<ul>
<li>all containers are in running state</li>
<li>no crashes in initial logs</li>
<li>shared volume mounts correctly configured</li>
</ul>

</div>

<h2>2. Authentication test (api_gateway)</h2>

<div class="service-box">

<p>
This phase validates the JWT authentication system shared between microservices.
</p>

Expected:

<ul>
<li>persistent user creation in SQLite</li>
<li>valid token generation</li>
<li>REST endpoint protection</li>
<li>SECRET_KEY consistency across services</li>
</ul>

<p class="note">
This test ensures session isolation and secure access to the diagnostic pipeline.
</p>

</div>

<h2>3. Orchestrator pipeline test</h2>

<div class="service-box">

<p>
The orchestrator service coordinates asynchronous execution of the radiomics pipeline.
</p>

Checks:

<ul>
<li>MRI task creation</li>
<li>correct state transitions</li>
<li>pipeline error propagation</li>
<li>concurrent job handling</li>
</ul>

Expected flow:

<div class="codeblock">
pending → running → completed
</div>

Failure case:

invalid MRI → status = failed

</div>

<h2>4. nextflow_worker pipeline test</h2>

<div class="service-box">

<p>
Verifies full execution of the automated neuroimaging pipeline.
</p>

Pipeline:

<div class="codeblock">
FreeSurfer / FastSurfer → ROI extraction → PyRadiomics → CSV generation
</div>

Expected outputs:

<ul>
<li>correct cortical segmentations</li>
<li>ROI masks generated</li>
<li>complete radiomics dataset</li>
</ul>

Required files:

<div class="codeblock">
ROI_labels.tsv
pyradiomics.yaml
</div>

</div>

<h2>5. model_service test</h2>

<div class="service-box">

<p>
Validates integration with the MLflow Model Registry on the DagsHub backend.
</p>

Expected:

<ul>
<li>connection to tracking server</li>
<li>champion model download</li>
<li>local cache correctly created</li>
<li>feature vector compatibility</li>
</ul>

</div>

<h2>6. inference_engine test</h2>

<div class="service-box">

<p>
The inference_engine service implements KNN classification and three-dimensional UMAP projection.
</p>

Expected outputs:

<div class="codeblock">
diagnosis_class
probability
umap_coordinates
</div>

Robustness tests:

<ul>
<li>missing features → controlled error</li>
<li>dimension mismatch → pipeline abort</li>
<li>incomplete dataset → fallback logging</li>
</ul>

</div>

<h2>7. llm_service test</h2>

<div class="service-box">

<p>
Validates generation of contextualized clinical explanations through Spatial RAG.
</p>

Checks:

<ul>
<li>embedding-aware responses</li>
<li>use of UMAP coordinates</li>
<li>access to relevant radiomic features</li>
<li>conversational memory persistence</li>
</ul>

Access without token:

Expected:

<div class="codeblock">
401 Unauthorized
</div>

</div>

<h2>8. React dashboard frontend test</h2>

<div class="service-box">

<p>
Verifies correct integration between the clinical UI and backend microservices.
</p>

Verified components:

<ul>
<li>Login.jsx → authentication</li>
<li>UploadZone.jsx → MRI submission</li>
<li>NiiVue.jsx → volumetric rendering</li>
<li>UmapPlot.jsx → latent space visualization</li>
<li>TaskHistory.jsx → analysis history</li>
</ul>

</div>

<h2>9. End-to-end integration test</h2>

<div class="service-box">

Complete workflow:

<div class="codeblock">
Login
Upload MRI
Segmentation
Radiomics extraction
KNN inference
UMAP embedding
Dashboard visualization
LLM assistant query
</div>

Expected:

pipeline completed without errors
consistent output across services
consistent UI visualization

</div>

<h2>10. Security test</h2>

<div class="service-box">

Checks:

<ul>
<li>JWT token validation</li>
<li>user data isolation</li>
<li>sensitive API key protection</li>
<li>no credential exposure in frontend</li>
</ul>

Protected keys:

<div class="codeblock">
GROQ_API_KEY
DAGSHUB_TOKEN
</div>

</div>

<h2>11. Performance test</h2>

<div class="service-box">

<table>

<tr>
<th>Component</th>
<th>Metric</th>
<th>Target</th>
</tr>

<tr>
<td>Segmentation</td>
<td>execution time</td>
<td>≤ hardware baseline</td>
</tr>

<tr>
<td>Radiomics</td>
<td>extraction time</td>
<td>parallelization active</td>
</tr>

<tr>
<td>Inference</td>
<td>latency</td>
<td>&lt; 1 second</td>
</tr>

<tr>
<td>LLM</td>
<td>response time</td>
<td>&lt; 2 seconds</td>
</tr>

<tr>
<td>MRI Viewer</td>
<td>rendering fps</td>
<td>smooth on modern browser</td>
</tr>

</table>

</div>

<h2>12. Environment compatibility test</h2>

<div class="service-box">

CPU-only:

<div class="codeblock">
params.brain_segmenter=freesurfer
</div>

GPU mode:

<div class="codeblock">
params.brain_segmenter=fastsurfer
</div>

Expected:

pipeline functional in both scenarios.

</div>

<h2>13. Error resilience test</h2>

<div class="service-box">

<table>

<tr>
<th>Simulated error</th>
<th>Expected</th>
</tr>

<tr>
<td>corrupted MRI</td>
<td>controlled pipeline abort</td>
</tr>

<tr>
<td>MLflow offline</td>
<td>managed fallback error</td>
</tr>

<tr>
<td>R service offline</td>
<td>task marked failed</td>
</tr>

<tr>
<td>Docker image missing</td>
<td>warning + pipeline stop</td>
</tr>

</table>

</div>

<h2>14. Environment variable configuration test</h2>

<div class="service-box">

<table>

<tr>
<th>Variable</th>
<th>Expected</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>consistent inter-service authentication</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>LLM active</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>registry reachable</td>
</tr>

<tr>
<td>HOST_SHARED_VOLUME_DIR</td>
<td>mount correctly configured</td>
</tr>

</table>

</div>

</div>

</body>
</html>