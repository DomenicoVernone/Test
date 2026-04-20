<style>
.varbox {
  border-left: 6px solid #ff9800;
  background: #fff7e6;
  padding: 12px;
  margin: 14px 0;
  border-radius: 6px;
}

.code {
  font-family: monospace;
  background: #eeeeee;
  padding: 6px 10px;
  border-radius: 4px;
  white-space: pre;
}

.section {
  margin-top: 26px;
}
</style>


<h1>Configurazione avanzata</h1>

Questa sezione descrive le principali variabili di configurazione utilizzate dalla piattaforma ClinicalTwin.

<div class="varbox">
Le variabili di configurazione sono definite nei file <span class="code">.env</span> dei microservizi.
</div>

Le impostazioni consentono di personalizzare autenticazione, pipeline radiomica, gestione modelli e servizi AI.


<h2>Autenticazione JWT</h2>

Le variabili seguenti devono essere identiche nei servizi che utilizzano JWT.

Variabile:

<div class="code">
SECRET_KEY=my_super_secret_key
</div>

Servizi coinvolti:

<ul>
<li>api_gateway</li>
<li>orchestrator</li>
<li>llm_service</li>
</ul>

Descrizione:

Chiave utilizzata per la firma dei token JWT. Deve essere condivisa tra i servizi per garantire autenticazione coerente tra microservizi.


<h2>Configurazione assistente AI</h2>

Variabile:

<div class="code">
GROQ_API_KEY=your_api_key_here
</div>

Servizio:

<ul>
<li>llm_service</li>
</ul>

Descrizione:

Chiave API utilizzata per accedere ai modelli linguistici tramite piattaforma Groq.

Senza questa variabile l’assistente clinico non sarà disponibile nella dashboard.


<h2>Configurazione Model Registry (MLflow + DagsHub)</h2>

Variabili richieste:

<div class="code">
MLFLOW_TRACKING_URI
MLFLOW_TRACKING_USERNAME
DAGSHUB_TOKEN
REPO_OWNER
REPO_NAME
</div>

Descrizione:

Consentono l’integrazione con MLflow Model Registry remoto per il versionamento dei modelli diagnostici.

Esempio:

<div class="code">
MLFLOW_TRACKING_URI=https://dagshub.com/&lt;user&gt;/&lt;repo&gt;.mlflow
</div>


<h2>Configurazione GPU (opzionale)</h2>

Variabile:

<div class="code">
MIG_DEVICE=MIG-xxxxxxxxxxxxxxxx
</div>

Descrizione:

UUID della MIG instance GPU utilizzata da FastSurfer.

Se non impostata:

<ul>
<li>viene utilizzata GPU standard</li>
<li>oppure CPU tramite FreeSurfer</li>
</ul>


<h2>Configurazione volumi condivisi</h2>

Variabile:

<div class="code">
HOST_SHARED_VOLUME_DIR=/mnt/shared_volume
</div>

Descrizione:

Percorso host utilizzato per la condivisione dati tra container.

Uso consigliato:

<ul>
<li>Linux bare metal → impostare manualmente</li>
<li>Docker Desktop (Windows/macOS) → lasciare vuoto</li>
</ul>


<h2>Configurazione pipeline Nextflow</h2>

File di configurazione:

<div class="code">
nextflow_worker/nextflow/configs/nextflow.config
</div>

Principali parametri disponibili:


<h3>Segmentatore anatomico</h3>

<div class="code">
params.brain_segmenter = freesurfer
</div>

Opzioni disponibili:

<ul>
<li>freesurfer</li>
<li>fastsurfer</li>
</ul>

Default:

<ul>
<li>freesurfer</li>
</ul>


<h3>Parallelismo pipeline</h3>

<div class="code">
params.maxforks = 1
</div>

Numero massimo di pipeline eseguibili in parallelo.


<h3>Thread FastSurfer</h3>

<div class="code">
params.fastsurfer_threads = 8
</div>

Numero thread CPU utilizzati da FastSurfer.


<h3>Parallelismo PyRadiomics</h3>

<div class="code">
params.pyradiomics_jobs = 4
</div>

Numero processi paralleli per estrazione radiomica.


<h2>Configurazione file radiomici esterni</h2>

Directory richiesta:

<div class="code">
nextflow_worker/data/external/
</div>

File necessari:

<ul>
<li><strong>ROI_labels.tsv</strong> — etichette delle 78 ROI cerebrali</li>
<li><strong>pyradiomics.yaml</strong> — parametri estrazione feature</li>
</ul>

Questi file sono necessari per l’esecuzione della pipeline radiomica.


<h2>Configurazione privacy e sicurezza</h2>

ClinicalTwin supporta ambienti di ricerca clinica sperimentale tramite:

<ul>
<li>autenticazione JWT</li>
<li>isolamento container Docker</li>
<li>gestione separata Model Registry</li>
<li>accesso controllato ai servizi LLM</li>
</ul>

L’utilizzo in ambiente clinico reale richiede integrazione con sistemi conformi alle normative GDPR e infrastrutture sanitarie certificate.