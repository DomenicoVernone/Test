<!DOCTYPE html>

<html lang="it">

<head>
<meta charset="UTF-8">
<title>MLOps – Introduction</title>

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

<h1>Introduction</h1>

<div class="section">
<h2>1. System Overview</h2>

<p>
MLOps is an advanced clinical decision support platform designed
for the differential diagnosis of Frontotemporal Dementia (FTD)
variants through automated analysis of magnetic resonance imaging (MRI).
</p>

<p>
The system integrates a complete pipeline for neuroimaging processing,
radiomic feature extraction, statistical inference, and AI-assisted
interpretation, following MLOps principles of reproducibility,
scalability, and modularity.
</p>

<p>
The objective is to transform complex data into interpretable clinical
information, supporting the medical decision-making process.
</p>

</div>

<div class="section">
<h2>2. Logical Architecture</h2>

<p>
The platform is built on a containerized microservices architecture,
where each component implements a specific responsibility within
the diagnostic workflow.
</p>

<ul>
<li><b>Neuroimaging pipeline</b> (Nextflow)</li>
<li><b>Orchestrator</b> (task management)</li>
<li><b>Model Service</b> (MLflow)</li>
<li><b>Inference Engine</b> (KNN + UMAP)</li>
<li><b>LLM Service</b> (Explainability)</li>
<li><b>React Frontend</b></li>
</ul>

<p>
This separation enables scalability and ease of extension.
</p>

</div>

<div class="section">
<h2>3. End-to-End Workflow</h2>

<p>
The system implements an automated workflow from MRI input to diagnosis.
</p>

<pre>
1. MRI Upload
2. API Gateway (JWT)
3. Orchestrator
4. Nextflow Pipeline
5. Radiomics Features (CSV)
6. Model Service
7. Inference Engine
8. UMAP Projection
9. LLM Explainability
10. Visualization
</pre>

<p>
The workflow ensures consistency and reproducibility of analyses.
</p>

</div>

<div class="section">
<h2>4. Neuroimaging and Radiomics Pipeline</h2>

<p>
The pipeline executes a deterministic sequence:
</p>

<ul>
<li>segmentation (FreeSurfer / FastSurfer)</li>
<li>ROI extraction</li>
<li>radiomic feature extraction (PyRadiomics)</li>
</ul>

<p>
The output is a feature vector used for inference.
</p>

</div>

<div class="section">
<h2>5. Inference and Explainability</h2>

<p>
The system uses:
</p>

<ul>
<li>KNN for classification</li>
<li>UMAP for 3D embedding</li>
</ul>

<p>
The LLM provides interpretations based on features and context.
</p>

</div>

<div class="section">
<h2>6. Key Features</h2>

<ul>
<li>Fully automated MRI pipeline</li>
<li>Microservices architecture</li>
<li>Reproducibility with Nextflow</li>
<li>MLflow integration</li>
<li>AI-based explainability</li>
</ul>

</div>

<div class="section">
<h2>7. Application Context</h2>

<p>
The platform is developed in an academic context for research
in neuroimaging and decision support systems.
</p>

<p>
It is not intended for direct clinical use without regulatory validation.
</p>

</div>

</div>

</body>

</html>
