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

/* ===== SERVICE BOX ===== */

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
Docs » Installation
</div>

<h1>Installation</h1>


<h2>GitHub</h2>

<div class="service-box">

<p>
Il codice sorgente di Clinical Twin è disponibile su GitHub. Il repository
include tutti i microservizi della piattaforma, la pipeline di neuroimaging
basata su Nextflow, i modelli di inferenza statistica e la dashboard clinica
per l’esplorazione dello spazio diagnostico latente.
</p>

<div class="codeblock">
https://github.com/carlosto033/Tesi-FTD.git
</div>

<p>Clonare il repository localmente:</p>

<div class="codeblock">
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
</div>

</div>


<h2>Prerequisites</h2>

<div class="service-box">

<p>
Prima dell’avvio della piattaforma è necessario configurare l’ambiente
di esecuzione installando i componenti richiesti per la gestione dei
container Docker e l’esecuzione della pipeline di segmentazione MRI.
</p>

<ul>
<li>Docker – esecuzione dei microservizi containerizzati</li>
<li>Docker Compose – orchestrazione dello stack applicativo</li>
<li>Git – clonazione del repository sorgente</li>
<li>NVIDIA GPU (opzionale) – accelerazione FastSurfer</li>
<li>WSL2 + CUDA drivers (Windows) – supporto GPU in ambiente Docker</li>
<li>FreeSurfer license file – necessario per la segmentazione anatomica</li>
</ul>

<div class="codeblock">
https://surfer.nmr.mgh.harvard.edu/registration.html
</div>

<p>
Il file di licenza FreeSurfer è obbligatorio per eseguire correttamente
la fase di segmentazione cerebrale della pipeline neuroimaging.
</p>

</div>


<h2>Environment configuration</h2>

<div class="service-box">

<p>
Clinical Twin utilizza file <code>.env</code> dedicati per ogni microservizio
al fine di configurare parametri di autenticazione, accesso ai modelli,
endpoint di inferenza e integrazione con servizi esterni.
</p>

<p>
Copiare i template forniti e personalizzarli prima dell’avvio dello stack:
</p>

<div class="codeblock">
cp .env.example .env
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp model_service/.env.example model_service/.env
cp llm_service/.env.example llm_service/.env
cp frontend/.env.example frontend/.env
</div>

</div>


<h2>Main variables</h2>

<div class="service-box">

<p>
Le variabili seguenti rappresentano i parametri principali utilizzati
per autenticazione tra microservizi, accesso al registry dei modelli
e integrazione con il servizio di inferenza AI.
</p>

<table>

<tr>
<th>Variable</th>
<th>Service</th>
<th>Description</th>
</tr>

<tr>
<td>SECRET_KEY</td>
<td>api_gateway, orchestrator, llm_service</td>
<td>Chiave condivisa per la generazione e validazione dei token JWT tra i microservizi</td>
</tr>

<tr>
<td>GROQ_API_KEY</td>
<td>llm_service</td>
<td>Chiave di accesso al servizio LLM utilizzato dall’assistente AI context-aware</td>
</tr>

<tr>
<td>MLFLOW_TRACKING_URI</td>
<td>model_service</td>
<td>Endpoint del server MLflow per il recupero dei modelli registrati</td>
</tr>

<tr>
<td>DAGSHUB_TOKEN</td>
<td>model_service</td>
<td>Token di autenticazione per l’accesso al Model Registry ospitato su DagsHub</td>
</tr>

</table>

</div>


<h2>FreeSurfer license</h2>

<div class="service-box">

<p>
La pipeline di segmentazione cerebrale richiede la presenza del file
di licenza FreeSurfer nella directory del worker Nextflow. Senza questo
file la fase di preprocessing MRI non può essere eseguita.
</p>

<div class="codeblock">
cp /path/to/license.txt nextflow_worker/license.txt
</div>

</div>


<h2>Build Docker images</h2>

<div class="service-box">

<p>
Questi comandi costruiscono le immagini Docker necessarie per eseguire
i moduli della pipeline radiomica, inclusi segmentazione anatomica,
preprocessing volumetrico e estrazione delle feature PyRadiomics.
</p>

<div class="codeblock">

docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</div>

</div>


<h2>Start the stack</h2>

<div class="service-box">

<p>
L’avvio dello stack Docker inizializza tutti i microservizi della piattaforma,
inclusi API Gateway, orchestrator, pipeline Nextflow, inference engine,
servizio LLM e interfaccia frontend.
</p>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Una volta completato l’avvio dei container, la dashboard clinica sarà
disponibile all’indirizzo:
</p>

<div class="codeblock">
http://localhost:5173
</div>

</div>


<h2>Create first user</h2>

<div class="service-box">

<p>
Al primo avvio della piattaforma è necessario registrare un utente tramite
Swagger UI esposto dall’API Gateway. Questo consente l’accesso alla dashboard
clinica e l’avvio delle analisi radiomiche.
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>Eseguire la richiesta:</p>

<div class="codeblock">
POST /signup
</div>

<p>
Dopo la registrazione sarà possibile autenticarsi e utilizzare la piattaforma
per l’analisi automatizzata delle immagini MRI.
</p>

</div>


</div>

</body>
</html>