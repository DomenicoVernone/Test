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

<h1>Piano di test completo – Clinical Twin</h1>

<div class="service-box">

<p>
Questo piano di test definisce le procedure di validazione funzionale, strutturale e prestazionale della piattaforma <strong>ClinicalTwin</strong>.
</p>

<p>
Le verifiche coprono l’intero stack applicativo, inclusi:
</p>

<ul>
<li>microservizi backend containerizzati</li>
<li>pipeline neuroimaging Nextflow</li>
<li>motore statistico di inferenza (KNN + UMAP)</li>
<li>model registry MLflow</li>
<li>assistente LLM Spatial RAG</li>
<li>dashboard clinica React</li>
</ul>

<p class="note">
L’obiettivo del test plan è garantire correttezza computazionale, robustezza operativa e riproducibilità del workflow diagnostico.
</p>

</div>

<h2>1. Test deployment dello stack Docker</h2>

<div class="service-box">

<p>
Questa fase verifica la corretta costruzione delle immagini container e l’avvio dell’intera architettura a microservizi.
</p>

<h3>Build immagini pipeline scientifica</h3>

<div class="codeblock">
docker build -t clinical-freesurfer ...
docker build -t clinical-fsl ...
docker build -t clinical-pyradiomics ...
</div>

<p>
Expected:
</p>

<ul>
<li>assenza errori durante la build</li>
<li>presenza immagini nel registry locale Docker</li>
<li>compatibilità runtime con Nextflow</li>
</ul>

<h3>Avvio stack</h3>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Verifica:
</p>

<ul>
<li>tutti i container risultano in stato running</li>
<li>assenza crash nei log iniziali</li>
<li>mount dei volumi condivisi correttamente eseguito</li>
</ul>

</div>

<h2>2. Test autenticazione (api_gateway)</h2>

<div class="service-box">

<p>
Questa fase valida il sistema di autenticazione JWT condiviso tra i microservizi.
</p>

Expected:

<ul>
<li>creazione utente persistente su SQLite</li>
<li>generazione token valido</li>
<li>protezione endpoint REST</li>
<li>coerenza SECRET_KEY tra servizi</li>
</ul>

<p class="note">
Il test garantisce isolamento delle sessioni e accesso sicuro alla pipeline diagnostica.
</p>

</div>

<h2>3. Test orchestrator pipeline</h2>

<div class="service-box">

<p>
Il servizio orchestrator coordina l’esecuzione asincrona della pipeline radiomica.
</p>

Verifiche:

<ul>
<li>creazione task MRI</li>
<li>transizione stati corretta</li>
<li>propagazione errori pipeline</li>
<li>gestione job concorrenti</li>
</ul>

Flow atteso:

<div class="codeblock">
pending → running → completed
</div>

Failure case:

MRI non valida → status = failed

</div>

<h2>4. Test pipeline nextflow_worker</h2>

<div class="service-box">

<p>
Verifica l’esecuzione completa della pipeline neuroimaging automatizzata.
</p>

Pipeline:

<div class="codeblock">
FreeSurfer / FastSurfer → ROI extraction → PyRadiomics → CSV generation
</div>

Output attesi:

<ul>
<li>segmentazioni corticali corrette</li>
<li>maschere ROI generate</li>
<li>dataset radiomico completo</li>
</ul>

File richiesti:

<div class="codeblock">
ROI_labels.tsv
pyradiomics.yaml
</div>

</div>

<h2>5. Test model_service</h2>

<div class="service-box">

<p>
Valida l’integrazione con MLflow Model Registry su backend DagsHub.
</p>

Expected:

<ul>
<li>connessione al tracking server</li>
<li>download modello champion</li>
<li>cache locale creata correttamente</li>
<li>compatibilità feature vector</li>
</ul>

</div>

<h2>6. Test inference_engine</h2>

<div class="service-box">

<p>
Il servizio inference_engine implementa classificazione KNN e proiezione UMAP tridimensionale.
</p>

Output attesi:

<div class="codeblock">
diagnosis_class
probability
umap_coordinates
</div>

Test robustezza:

<ul>
<li>feature mancanti → errore controllato</li>
<li>dimension mismatch → pipeline abort</li>
<li>dataset incompleto → fallback logging</li>
</ul>

</div>

<h2>7. Test llm_service</h2>

<div class="service-box">

<p>
Valida la generazione di spiegazioni cliniche contestualizzate tramite Spatial RAG.
</p>

Verifiche:

<ul>
<li>risposte embedding-aware</li>
<li>uso coordinate UMAP</li>
<li>accesso feature radiomiche rilevanti</li>
<li>persistenza memoria conversazionale</li>
</ul>

Accesso senza token:

Expected:

<div class="codeblock">
401 Unauthorized
</div>

</div>

<h2>8. Test frontend React dashboard</h2>

<div class="service-box">

<p>
Verifica la corretta integrazione tra UI clinica e backend microservizi.
</p>

Componenti verificati:

<ul>
<li>Login.jsx → autenticazione</li>
<li>UploadZone.jsx → invio MRI</li>
<li>NiiVue.jsx → rendering volumetrico</li>
<li>UmapPlot.jsx → visualizzazione spazio latente</li>
<li>TaskHistory.jsx → storico analisi</li>
</ul>

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
output coerente tra servizi
visualizzazione consistente UI

</div>

<h2>10. Test sicurezza</h2>

<div class="service-box">

Verifiche:

<ul>
<li>validazione token JWT</li>
<li>isolamento dati utente</li>
<li>protezione API keys sensibili</li>
<li>assenza esposizione credenziali frontend</li>
</ul>

Chiavi protette:

<div class="codeblock">
GROQ_API_KEY
DAGSHUB_TOKEN
</div>

</div>

<h2>11. Test performance</h2>

<div class="service-box">

<table>

<tr>
<th>Componente</th>
<th>Metrica</th>
<th>Obiettivo</th>
</tr>

<tr>
<td>Segmentazione</td>
<td>tempo esecuzione</td>
<td>≤ baseline hardware</td>
</tr>

<tr>
<td>Radiomics</td>
<td>tempo estrazione</td>
<td>parallelizzazione attiva</td>
</tr>

<tr>
<td>Inferenza</td>
<td>latency</td>
<td>&lt; 1 secondo</td>
</tr>

<tr>
<td>LLM</td>
<td>response time</td>
<td>&lt; 2 secondi</td>
</tr>

<tr>
<td>Viewer MRI</td>
<td>fps rendering</td>
<td>fluido su browser moderno</td>
</tr>

</table>

</div>

<h2>12. Test compatibilità ambiente</h2>

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

pipeline funzionante in entrambi gli scenari.

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
<td>pipeline abort controllato</td>
</tr>

<tr>
<td>MLflow offline</td>
<td>fallback errore gestito</td>
</tr>

<tr>
<td>R service offline</td>
<td>task marked failed</td>
</tr>

<tr>
<td>Docker image missing</td>
<td>warning + stop pipeline</td>
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
<td>autenticazione inter-servizio coerente</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>LLM attivo</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>registry raggiungibile</td>
</tr>

<tr>
<td>HOST_SHARED_VOLUME_DIR</td>
<td>mount correttamente configurato</td>
</tr>

</table>

</div>

</div>

</body>
</html>
