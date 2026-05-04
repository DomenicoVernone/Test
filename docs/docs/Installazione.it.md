<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Installation</title>

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

<h1>Installazione della piattaforma MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
Questa sezione descrive i passaggi necessari per configurare
l’ambiente di esecuzione della piattaforma MLOps e avviare
lo stack completo dei microservizi.
</p>

<p>
L’installazione è progettata per essere semplice e riproducibile,
basata su container Docker e file di configurazione dedicati
per ciascun servizio.
</p>

</div>

<div class="section">
<h2>2. Repository</h2>

<p>
Il codice sorgente della piattaforma è disponibile su GitHub
e include tutti i microservizi, la pipeline Nextflow e la
dashboard frontend.
</p>

<pre>
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
</pre>

<p>
Il repository contiene:
</p>

<ul>
<li>microservizi backend</li>
<li>pipeline radiomica Nextflow</li>
<li>frontend React</li>
<li>file di configurazione Docker</li>
</ul>

</div>

<div class="section">
<h2>3. Prerequisiti</h2>

<p>
Prima dell’installazione è necessario disporre dei seguenti componenti:
</p>

<ul>
<li>Docker</li>
<li>Docker Compose</li>
<li>Git</li>
</ul>

<p>
Componenti opzionali:
</p>

<ul>
<li>GPU NVIDIA (per accelerazione FastSurfer)</li>
<li>CUDA + NVIDIA Container Toolkit</li>
</ul>

<p>
È inoltre necessario scaricare la licenza FreeSurfer:
</p>

<pre>
https://surfer.nmr.mgh.harvard.edu/registration.html
</pre>

</div>

<div class="section">
<h2>4. Configurazione ambiente</h2>

<p>
La piattaforma utilizza file <code>.env</code> per configurare
i parametri dei microservizi.
</p>

<p>
Copiare i file di esempio:
</p>

<pre>
cp .env.example .env
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp model_service/.env.example model_service/.env
cp llm_service/.env.example llm_service/.env
cp frontend/.env.example frontend/.env
</pre>
<p>
Successivamente configurare le principali variabili di ambiente utilizzate
per la comunicazione tra microservizi e l’integrazione con servizi esterni:
</p>

<table>

<tr>
<th>Variabile</th>
<th>Servizio</th>
<th>Descrizione</th>
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

<div class="section">
<h2>5. Licenza FreeSurfer</h2>

<p>
La pipeline di segmentazione richiede una licenza FreeSurfer valida.
</p>

<p>
Dopo aver scaricato il file:
</p>

<pre>
cp /path/to/license.txt nextflow_worker/license.txt
</pre>

<p>
Senza questo file la pipeline non può essere eseguita.
</p>

</div>

<div class="section">
<h2>6. Build immagini Docker</h2>

<p>
È necessario costruire le immagini utilizzate dalla pipeline radiomica.
</p>

<pre>
docker build -t clinical-freesurfer -f nextflow_worker/dockerfiles/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/dockerfiles/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/dockerfiles/pyradiomics.dockerfile nextflow_worker/
</pre>

<p>
Queste immagini verranno utilizzate automaticamente da Nextflow.
</p>

</div>

<div class="section">
<h2>7. Avvio dello stack</h2>

<p>
Una volta completata la configurazione, è possibile avviare
l’intero sistema.
</p>

<pre>
docker compose up -d --build
</pre>

<p>
Questo comando inizializza:
</p>

<ul>
<li>API Gateway</li>
<li>Orchestrator</li>
<li>Nextflow Worker</li>
<li>Inference Engine</li>
<li>LLM Service</li>
<li>Frontend</li>
</ul>

</div>

<div class="section">
<h2>8. Verifica installazione</h2>

<p>
Dopo l’avvio verificare:
</p>

<ul>
<li>container attivi (docker ps)</li>
<li>assenza errori nei log</li>
<li>frontend accessibile</li>
</ul>

<p>Accesso servizi:</p>

<pre>
Frontend → http://localhost:5173
Swagger → http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>9. Creazione primo utente</h2>

<p>
Al primo avvio è necessario creare un utente tramite API Gateway.
</p>

<pre>
POST /signup
</pre>

<p>
Dopo la registrazione sarà possibile accedere alla piattaforma
e avviare analisi MRI.
</p>

</div>

<div class="section">
<h2>10. Avvio prima analisi</h2>

<p>
Una volta effettuato il login:
</p>

<ul>
<li>caricare una MRI (.nii o .nii.gz)</li>
<li>avviare la pipeline</li>
<li>monitorare lo stato tramite dashboard</li>
</ul>

<p>
Il sistema eseguirà automaticamente:
</p>

<ul>
<li>segmentazione</li>
<li>estrazione radiomica</li>
<li>inferenza</li>
<li>visualizzazione risultati</li>
</ul>

</div>

<div class="section">
<h2>11. Conclusioni</h2>

<p>
L’installazione della piattaforma MLOps è progettata per essere
rapida e riproducibile grazie all’utilizzo di Docker e configurazioni
centralizzate.
</p>

<p>
Una volta completata, il sistema è pronto per eseguire pipeline
radiomiche complete e supportare workflow di analisi clinica.
</p>

</div>

</div>

</body>

</html>
