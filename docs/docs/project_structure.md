<style>

.section {

&#x20; border-left: 6px solid #009688;

&#x20; background: #eefaf8;

&#x20; padding: 12px;

&#x20; margin: 16px 0;

&#x20; border-radius: 6px;

}



.code {

&#x20; background: #eeeeee;

&#x20; font-family: monospace;

&#x20; padding: 6px;

&#x20; border-radius: 4px;

}

</style>



<h1>Struttura del Progetto</h1>



<div class="section">

ClinicalTwin è organizzato come architettura a microservizi containerizzati distribuiti tramite Docker Compose.

</div>



<h2>Struttura repository</h2>



<pre class="code">

Tesi-FTD/

├── docker-compose.yml

├── docs/

├── api\_gateway/

├── orchestrator/

├── model\_service/

├── inference\_engine/

├── llm\_service/

├── nextflow\_worker/

└── frontend/

</pre>



<h2>API Gateway</h2>



Responsabilità:



<ul>

<li>autenticazione utenti</li>

<li>generazione token JWT</li>

<li>protezione accesso API</li>

</ul>



<h2>Orchestrator</h2>



Coordina:



<ul>

<li>task MRI</li>

<li>pipeline Nextflow</li>

<li>model\_service</li>

</ul>



<h2>Model Service</h2>



Gestisce:



<ul>

<li>download modelli MLflow</li>

<li>versionamento modelli</li>

<li>inferenza radiomica</li>

</ul>



<h2>Inference Engine</h2>



Implementa:



<ul>

<li>KNN classification</li>

<li>UMAP embedding</li>

</ul>



<h2>LLM Service</h2>



Supporta:



<ul>

<li>interpretazione predizioni</li>

<li>Spatial RAG</li>

<li>memoria conversazionale</li>

</ul>



<h2>Nextflow Worker</h2>



Responsabile di:



<ul>

<li>segmentazione FreeSurfer</li>

<li>ROI extraction</li>

<li>radiomics extraction</li>

</ul>



<h2>Frontend</h2>



Funzioni:



<ul>

<li>upload MRI</li>

<li>viewer multiplanare</li>

<li>visualizzazione UMAP</li>

<li>assistente AI</li>

</ul>

