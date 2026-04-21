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

</style>

</head>

<body>

<div class="content">

<div class="breadcrumb">
Docs » Test Plan
</div>

<h1>Piano di test completo – Clinical Twin</h1>

<div class="service-box">

<p>
Questo piano di test definisce le procedure di validazione funzionale,
strutturale e prestazionale della piattaforma Clinical Twin, includendo
verifiche sui microservizi, pipeline neuroimaging, motore di inferenza,
assistente AI e dashboard clinica.
</p>

</div>


<h2>1. Test deployment dello stack Docker</h2>

<div class="service-box">

<h3>Build immagini pipeline</h3>

<div class="codeblock">
docker build -t clinical-freesurfer ...
docker build -t clinical-fsl ...
docker build -t clinical-pyradiomics ...
</div>

<p><b>Expected:</b> build completata senza errori e immagini presenti in docker images.</p>

<h3>Avvio stack</h3>

<div class="codeblock">
docker compose up -d --build
</div>

<p><b>Verifica servizi attivi:</b></p>

<ul>
<li>api_gateway → 8000</li>
<li>orchestrator → 8001</li>
<li>llm_service → 8002</li>
<li>model_service → 8003</li>
<li>inference_engine → 8004</li>
<li>nextflow_worker → 8005</li>
<li>frontend → 5173</li>
</ul>

</div>


<h2>2. Test autenticazione (api_gateway)</h2>

<div class="service-box">

<h3>Signup</h3>

Endpoint:

<div class="codeblock">
POST /signup
</div>

Expected:

utente salvato correttamente nel database SQLite.

<h3>Login</h3>

Endpoint:

<div class="codeblock">
POST /login
</div>

Expected:

token JWT valido restituito.

<h3>Endpoint protetti</h3>

Expected:

senza token → 401  
con token → 200

</div>


<h2>3. Test orchestrator pipeline</h2>

<div class="service-box">

<h3>Creazione task</h3>

Endpoint:

<div class="codeblock">
POST /analyze
</div>

Expected:

task_id generato  
stato iniziale = pending

<h3>Polling stato task</h3>

Endpoint:

<div class="codeblock">
GET /task/{id}
</div>

Flow atteso:

pending → running → completed

<h3>Failure handling</h3>

Input MRI non valido:

Expected:

status = failed

</div>


<h2>4. Test pipeline nextflow_worker</h2>

<div class="service-box">

Pipeline:

FreeSurfer / FastSurfer → PyRadiomics → feature table

Expected output directory:

<div class="codeblock">
segmentation/
stats/
labels/
</div>

Output radiomica:

<div class="codeblock">
radiomics_features.csv
</div>

Contenuti:

<ul>
<li>shape features</li>
<li>texture features</li>
<li>intensity features</li>
</ul>

Config richiesti:

<div class="codeblock">
ROI_labels.tsv
pyradiomics.yaml
</div>

</div>


<h2>5. Test model_service</h2>

<div class="service-box">

Trigger:

<div class="codeblock">
POST /predict
</div>

Expected:

download champion model  
cache locale creata  
registry MLflow raggiungibile

Variabili richieste:

MLFLOW_TRACKING_URI  
DAGSHUB_TOKEN

</div>


<h2>6. Test inference_engine</h2>

<div class="service-box">

Motore:

KNN + UMAP 3D

Output KNN:

<div class="codeblock">
diagnosis_class
probability
</div>

Output UMAP:

<div class="codeblock">
x
y
z
</div>

Test robustezza:

feature mancanti → errore controllato

</div>


<h2>7. Test llm_service</h2>

<div class="service-box">

Query:

<div class="codeblock">
Explain this cluster
</div>

Expected:

risposta embedding-aware

Test memoria multi-turno:

Q1 → Q2 follow-up

Expected:

persistenza contesto conversazionale

Accesso senza token:

Expected:

401 Unauthorized

</div>


<h2>8. Test frontend React dashboard</h2>

<div class="service-box">

Login UI:

Expected:

redirect automatico alla dashboard

Upload MRI:

UploadZone.jsx → task backend creato

Viewer MRI:

NiiVue.jsx → rendering sagittale / coronale / assiale

Spazio latente:

UmapPlot.jsx → scatter 3D interattivo

Storico analisi:

TaskHistory.jsx → lista task precedenti

</div>


<h2>9. Test integrazione end-to-end</h2>

<div class="service-box">

Workflow completo:

<div class="codeblock">
Login
Upload MRI
Segmentazione
Radiomics extraction
Inferenza KNN
Embedding UMAP
Visualizzazione dashboard
Query LLM assistant
</div>

Expected:

pipeline completata senza errori

</div>


<h2>10. Test sicurezza</h2>

<div class="service-box">

JWT alterato:

Expected:

access denied

Access isolation:

Utente A ≠ Utente B

Expected:

isolamento task

Protezione API keys:

<div class="codeblock">
GROQ_API_KEY
DAGSHUB_TOKEN
</div>

Expected:

non esposte al frontend

</div>


<h2>11. Test performance</h2>

<div class="service-box">

<table>

<tr>
<th>Componente</th>
<th>Metrica</th>
</tr>

<tr>
<td>Segmentazione</td>
<td>tempo esecuzione</td>
</tr>

<tr>
<td>Radiomics</td>
<td>tempo estrazione</td>
</tr>

<tr>
<td>Inferenza</td>
<td>latency</td>
</tr>

<tr>
<td>LLM</td>
<td>response time</td>
</tr>

<tr>
<td>Viewer MRI</td>
<td>fps rendering</td>
</tr>

</table>

</div>


<h2>12. Test compatibilità ambiente</h2>

<div class="service-box">

CPU-only:

<div class="codeblock">
params.brain_segmenter=freesurfer
</div>

Expected:

pipeline funzionante

GPU mode:

<div class="codeblock">
params.brain_segmenter=fastsurfer
</div>

Expected:

accelerazione attiva

</div>


<h2>13. Test resilienza errori</h2>

<div class="service-box">

<table>

<tr>
<th>Errore simulato</th>
<th>Expected</th>
</tr>

<tr>
<td>MRI corrotta</td>
<td>pipeline abort</td>
</tr>

<tr>
<td>MLflow offline</td>
<td>errore controllato</td>
</tr>

<tr>
<td>R service offline</td>
<td>task failed</td>
</tr>

<tr>
<td>Docker image missing</td>
<td>warning log</td>
</tr>

</table>

</div>


<h2>14. Test configurazione variabili ambiente</h2>

<div class="service-box">

<table>

<tr>
<th>Variabile</th>
<th>Expected</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>autenticazione valida</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>LLM funzionante</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>registry raggiungibile</td>
</tr>

<tr>
<td>HOST_SHARED_VOLUME_DIR</td>
<td>mount corretto</td>
</tr>

</table>

</div>


</div>

</body>

</html>