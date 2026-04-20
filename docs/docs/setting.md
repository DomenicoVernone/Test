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
  background: #eee;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>

<h1>Configurazione Avanzata</h1>

<div class="varbox">
Le variabili di configurazione sono definite nei file <span class="code">.env</span> dei microservizi.
</div>

<h2>Autenticazione JWT</h2>

Variabile:

<pre>SECRET_KEY=my_super_secret_key</pre>

Servizi:

<ul>
<li>api_gateway</li>
<li>orchestrator</li>
<li>llm_service</li>
</ul>

<h2>Configurazione LLM</h2>

<pre>GROQ_API_KEY=your_api_key</pre>

Necessaria per attivare l’assistente AI.

<h2>Model Registry MLflow</h2>

Variabili richieste:

<pre>
MLFLOW_TRACKING_URI
MLFLOW_TRACKING_USERNAME
DAGSHUB_TOKEN
REPO_OWNER
REPO_NAME
</pre>

<h2>Configurazione GPU</h2>

<pre>MIG_DEVICE=MIG-xxxxxxxx</pre>

Opzionale.

<h2>Volumi condivisi</h2>

<pre>HOST_SHARED_VOLUME_DIR=/mnt/shared_volume</pre>

Necessario solo su Linux bare metal.

<h2>Configurazione Nextflow</h2>

File:

<pre>nextflow_worker/nextflow/configs/nextflow.config</pre>