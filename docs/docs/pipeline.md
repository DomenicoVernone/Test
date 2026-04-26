<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Pipeline Workflow</title>

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
Docs » Pipeline Workflow
</div>

<h1>Pipeline Workflow</h1>

<p>
This section describes the complete workflow of the Clinical Twin radiomics pipeline, from MRI acquisition to diagnostic prediction generation and visualization of results in the clinical dashboard.
</p>

<div class="service-box">

<p>
The Clinical Twin pipeline implements an automated radiomics analysis workflow
on structural T1-weighted magnetic resonance images aimed at differential
diagnosis of Frontotemporal Dementia (FTD) variants.
</p>

<p>
Execution is orchestrated by the <b>orchestrator</b> microservice, while
computational processing is handled through <b>Nextflow</b> within
the <b>nextflow_worker</b> service, ensuring parallelization,
reproducibility, and scalability of the entire neuroimaging process.
</p>

</div>


<h2>Pipeline overview</h2>

<div class="service-box">

<p>
The operational flow of the pipeline follows a structured sequence of
volumetric transformations, radiomic biomarker extraction, and
statistical inference in the diagnostic latent space.
</p>

<div class="codeblock">
MRI → Preprocessing → Segmentation → ROI Extraction → Radiomics → KNN Inference → UMAP Embedding → Dashboard
</div>

</div>


<h2>1. MRI upload</h2>

<div class="service-box">

<p>
The user uploads a structural brain MRI through the clinical dashboard.
Data are stored in the shared Docker volume and registered as an
asynchronous task managed by the orchestrator.
</p>

<p>Supported formats:</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
This phase represents the entry point of the neuroimaging pipeline.
</p>

</div>


<h2>2. Volumetric preprocessing</h2>

<div class="service-box">

<p>
Preprocessing prepares the MRI volume for standardized anatomical segmentation
and radiomic feature extraction.
</p>

<ul>
<li>voxel intensity normalization</li>
<li>isotropic volume resampling</li>
<li>stereotactic spatial alignment</li>
<li>MRI dataset integrity verification</li>
</ul>

<p>
These operations reduce inter-scanner variability and improve the
robustness of extracted features.
</p>

</div>


<h2>3. Anatomical segmentation</h2>

<div class="service-box">

<p>
Brain segmentation enables cortical parcellation into standardized
anatomical regions suitable for region-based radiomic analysis.
</p>

<p>Tools used:</p>

<ul>
<li>FreeSurfer (CPU mode)</li>
<li>FastSurfer (optional GPU mode)</li>
</ul>

<p>
The output consists of volumetric labeling maps of cortical
and subcortical ROIs.
</p>

</div>


<h2>4. Brain ROI extraction</h2>

<div class="service-box">

<p>
Segmented anatomical regions are associated with standard labels
through the mapping table used by the pipeline.
</p>

<div class="codeblock">
ROI_labels.tsv
</div>

<p>
This phase enables construction of a structured dataset for
regional radiomic feature extraction.
</p>

</div>


<h2>5. Radiomic feature extraction</h2>

<div class="service-box">

<p>
Radiomic features are extracted using <b>PyRadiomics</b> with
a parametric configuration defined in the pipeline YAML file.
</p>

<div class="codeblock">
pyradiomics.yaml
</div>

<p>Main extracted features:</p>

<ul>
<li>first-order intensity statistics</li>
<li>GLCM texture features</li>
<li>GLRLM texture features</li>
<li>GLSZM texture features</li>
<li>three-dimensional shape descriptors</li>
</ul>

<p>
These features represent quantitative biomarkers used for
diagnostic classification.
</p>

</div>


<h2>6. Statistical inference</h2>

<div class="service-box">

<p>
Radiomic features are sent to the <b>inference_engine</b> microservice,
which performs diagnostic classification in feature space.
</p>

<ul>
<li>classification using the K-Nearest Neighbors (KNN) algorithm</li>
<li>similarity computation with patients in the reference dataset</li>
<li>probabilistic estimation of the FTD diagnostic class</li>
</ul>

<p>
This phase represents the decision-making core of the Clinical Twin system.
</p>

</div>


<h2>7. Projection into the UMAP latent space</h2>

<div class="service-box">

<p>
Features are projected into a three-dimensional latent space using
UMAP to enable visual exploration of patient distribution.
</p>

<ul>
<li>visualization of clinical sample distribution</li>
<li>identification of diagnostic clusters</li>
<li>search for clinically similar nearest neighbors</li>
</ul>

<p>
The UMAP space forms the basis of the visual explainability model.
</p>

</div>


<h2>8. Results visualization</h2>

<div class="service-box">

<p>
Results are made available in the interactive React dashboard
to support clinical analysis of the patient case.
</p>

<ul>
<li>multiplanar segmentation of brain ROIs (NiiVue)</li>
<li>patient position in UMAP latent space</li>
<li>estimated diagnostic class</li>
<li>classifier confidence score</li>
<li>clinically similar nearest neighbors</li>
</ul>

</div>


<h2>9. Interpretation through the AI assistant</h2>

<div class="service-box">

<p>
The context-aware AI assistant uses a Spatial-RAG approach to
interpret radiomic results and provide clinically contextualized
explanations of the patient’s position in the diagnostic space.
</p>

<p>
This module improves model interpretability and supports the
medical decision-making process.
</p>

</div>



</div>

</body>
</html>