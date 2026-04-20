<style>

.api-box {

&#x20; border-left: 6px solid #607d8b;

&#x20; background: #eef3f6;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

}

.endpoint {

&#x20; font-family: monospace;

&#x20; background: #f4f4f4;

&#x20; padding: 6px;

&#x20; border-radius: 4px;

}

</style>



<h1>API Documentation</h1>



<div class="api-box">

ClinicalTwin espone REST API distribuite su microservizi containerizzati.

</div>



<h2>Servizi disponibili</h2>



<ul>

<li>api\_gateway — autenticazione</li>

<li>orchestrator — gestione pipeline</li>

<li>nextflow\_worker — preprocessing MRI</li>

<li>model\_service — classificazione</li>

<li>inference\_engine — inferenza UMAP</li>

<li>llm\_service — assistente AI</li>

</ul>



<h2>Autenticazione</h2>



Endpoint:



<div class="endpoint">POST /login</div>



Restituisce:



JWT token



Header richiesto:



<div class="endpoint">

Authorization: Bearer \&lt;JWT\_TOKEN\&gt;

</div>



<h2>Upload MRI</h2>



<div class="endpoint">

POST /analyze/

</div>



Avvia pipeline radiomica.



<h2>Inferenza diagnostica</h2>



<div class="endpoint">

POST /predict

</div>



Restituisce:



<ul>

<li>classe predetta</li>

<li>confidence</li>

<li>coordinate UMAP</li>

</ul>



<h2>Assistente clinico</h2>



<div class="endpoint">

POST /chat

</div>



Permette interpretazione context-aware dei risultati diagnostici.

