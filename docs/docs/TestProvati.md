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

.status-pass { color: green; font-weight: bold; }
.status-run { color: orange; font-weight: bold; }
.status-fail { color: red; font-weight: bold; }

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
Questo piano di test descrive in modo sistematico la validazione funzionale, strutturale e prestazionale della piattaforma <strong>ClinicalTwin</strong>, verificando il corretto funzionamento dell’intera pipeline diagnostica automatizzata basata su neuroimaging strutturale, radiomica e modelli di machine learning.
</p>

<p>
Le verifiche coprono:
</p>

<ul>
<li>microservizi backend containerizzati orchestrati tramite Docker Compose</li>
<li>pipeline neuroimaging Nextflow (FreeSurfer / FastSurfer)</li>
<li>estrazione feature radiomiche PyRadiomics</li>
<li>motore inferenziale KNN + UMAP</li>
<li>registry MLflow su DagsHub</li>
<li>assistente clinico LLM Spatial RAG</li>
<li>dashboard clinica React</li>
</ul>

<p class="note">
Obiettivo: garantire correttezza computazionale, robustezza operativa, sicurezza dei dati e riproducibilità scientifica del workflow diagnostico.
</p>

</div>

<h2>1. Test deployment dello stack Docker <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

<p>
Verifica della corretta costruzione delle immagini container scientifiche e dell’avvio coordinato dell’architettura a microservizi.
</p>

<p>
Durante il test sono stati controllati:
</p>

<ul>
<li>build corretta immagini FreeSurfer, Nextflow worker e servizi backend</li>
<li>avvio orchestrato tramite docker compose</li>
<li>assenza crash nei container</li>
<li>corretto mapping porte e volumi condivisi</li>
</ul>

<p>
Tutti i container risultano attivi tramite comando:
</p>

<div class="codeblock">
docker ps
</div>

</div>

<h2>2. Test autenticazione (api_gateway) <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

<p>
Verifica del sistema di autenticazione JWT condiviso tra i microservizi backend.
</p>

Verifiche eseguite:

<ul>
<li>generazione token valida dopo login</li>
<li>protezione endpoint REST tramite header Authorization</li>
<li>rifiuto richieste senza token (errore 401)</li>
<li>coerenza SECRET_KEY tra servizi</li>
</ul>

<p>
Accesso diretto endpoint orchestrator senza token produce correttamente:
</p>

<div class="codeblock">
{"detail":"Not authenticated"}
</div>

</div>

<h2>3. Test orchestrator pipeline <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

<p>
Validazione del servizio orchestrator responsabile della gestione asincrona delle pipeline di elaborazione MRI.
</p>

Verifiche effettuate:

<ul>
<li>creazione task analisi MRI</li>
<li>polling stato pipeline funzionante</li>
<li>transizione stato pending → processing corretta</li>
<li>sincronizzazione con frontend dashboard</li>
</ul>

Risposta endpoint verificata:

<div class="codeblock">
/analyze/status/{id} → PROCESSING
</div>

</div>

<h2>4. Test pipeline nextflow_worker <span class="status-run">[IN CORSO]</span></h2>

<div class="service-box">

<p>
Verifica esecuzione pipeline neuroimaging automatizzata tramite Nextflow DSL2.
</p>

Pipeline attiva:

<div class="codeblock">
FreeSurfer → ROI extraction → PyRadiomics → CSV generation
</div>

Step completati finora:

<ul>
<li>conversione MRI con mri_convert</li>
<li>Talairach registration</li>
<li>bias field correction</li>
<li>avvio segmentazione recon-all</li>
</ul>

Output attesi al termine:

<div class="codeblock">
labels/
stats/
radiomics_features.csv
</div>

</div>

<h2>5. Test model_service <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

<p>
Validazione integrazione con MLflow Model Registry ospitato su DagsHub.
</p>

Verifiche previste:

<ul>
<li>connessione tracking server MLflow</li>
<li>download modello champion</li>
<li>creazione cache locale modello</li>
<li>compatibilità feature radiomiche input</li>
</ul>

Test non ancora eseguito poiché inferenza non completata.

</div>

<h2>6. Test inference_engine <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

<p>
Validazione classificazione automatica tramite algoritmo KNN e proiezione nello spazio latente UMAP tridimensionale.
</p>

Output attesi:

<div class="codeblock">
diagnosis_class
probability
umap_coordinates
</div>

Test verrà completato automaticamente al termine della pipeline radiomica.

</div>

<h2>7. Test llm_service <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

<p>
Verifica generazione spiegazioni cliniche contestualizzate tramite assistente Spatial RAG.
</p>

Verifiche previste:

<ul>
<li>uso embedding radiomici</li>
<li>integrazione coordinate UMAP</li>
<li>persistenza memoria conversazionale</li>
<li>protezione endpoint tramite JWT</li>
</ul>

Accesso senza token restituisce correttamente:

<div class="codeblock">
401 Unauthorized
</div>

Test conversazionale completo non ancora eseguito.

</div>

<h2>8. Test frontend React dashboard <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

<p>
Verifica integrazione frontend con orchestrator e servizi backend.
</p>

Componenti validati:

<ul>
<li>Login.jsx autenticazione funzionante</li>
<li>UploadZone.jsx invio MRI corretto</li>
<li>NiiVue.jsx rendering MPR corretto</li>
<li>TaskHistory.jsx sincronizzazione stato pipeline</li>
<li>polling realtime task status</li>
</ul>

</div>

<h2>9. Test integrazione end-to-end <span class="status-run">[IN CORSO]</span></h2>

<div class="service-box">

Workflow validato finora:

<div class="codeblock">
Login
Upload MRI
Segmentazione FreeSurfer
Tracking pipeline
Polling stato task
</div>

Workflow completo atteso:

<div class="codeblock">
Radiomics extraction
Inferenza KNN
Embedding UMAP
Visualizzazione dashboard
Query LLM assistant
</div>

</div>

<h2>10. Test sicurezza <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

Verifiche eseguite:

<ul>
<li>protezione endpoint REST con JWT</li>
<li>isolamento accesso utenti</li>
<li>assenza esposizione token lato frontend</li>
<li>protezione accesso orchestrator</li>
</ul>

Chiavi sensibili protette:

<div class="codeblock">
GROQ_API_KEY
DAGSHUB_TOKEN
</div>

</div>

<h2>11. Test performance <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

Test non ancora eseguito. Verranno misurati:

<ul>
<li>tempo segmentazione FreeSurfer</li>
<li>tempo estrazione radiomics</li>
<li>latenza inferenza KNN</li>
<li>tempo risposta LLM</li>
<li>fluidità rendering viewer MRI</li>
</ul>

</div>

<h2>12. Test compatibilità ambiente <span class="status-pass">[PASSATO]</span></h2>

<div class="service-box">

Pipeline verificata in modalità CPU-only:

<div class="codeblock">
params.brain_segmenter=freesurfer
</div>

Segmentazione avviata correttamente tramite container FreeSurfer.

Supporto GPU FastSurfer disponibile ma non testato in questa esecuzione.

</div>

<h2>13. Test resilienza errori <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

Test previsti ma non ancora eseguiti:

<ul>
<li>MRI corrotta</li>
<li>MLflow offline</li>
<li>inference_engine offline</li>
<li>container mancanti</li>
</ul>

</div>

<h2>14. Test configurazione variabili ambiente <span class="status-fail">[Ancora da Testare]</span></h2>

<div class="service-box">

Variabili da validare:

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