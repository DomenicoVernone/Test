<style>

.api-box {

&#x20; border-left: 6px solid #607d8b;

&#x20; background: #eef3f6;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}



.endpoint {

&#x20; font-family: monospace;

&#x20; background: #f4f4f4;

&#x20; padding: 6px 10px;

&#x20; border-radius: 4px;

&#x20; display: inline-block;

}



.code {

&#x20; font-family: monospace;

&#x20; background: #eeeeee;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; white-space: pre;

}

</style>





<h1>API Documentation</h1>





<div class="api-box">



ClinicalTwin espone un insieme di REST API distribuite su più microservizi containerizzati. Le API consentono la gestione dell’autenticazione, l’avvio della pipeline neuroimaging, l’esecuzione dell’inferenza diagnostica e l’interazione con l’assistente clinico basato su modelli linguistici.



Le API sono documentate automaticamente tramite Swagger UI.



</div>





<h2>Servizi disponibili</h2>



<ul>

<li><strong>api\_gateway</strong> — porta 8000 — autenticazione utenti</li>

<li><strong>orchestrator</strong> — porta 8001 — gestione task pipeline</li>

<li><strong>llm\_service</strong> — porta 8002 — assistente AI</li>

<li><strong>model\_service</strong> — porta 8003 — gestione modelli ML</li>

<li><strong>inference\_engine</strong> — porta 8004 — inferenza statistica</li>

<li><strong>nextflow\_worker</strong> — porta 8005 — pipeline neuroimaging</li>

</ul>





<h2>API Gateway</h2>



Swagger UI:



<code>http://localhost:8000/docs</code>



Gestisce autenticazione e generazione token JWT.





<h3>Registrazione utente</h3>



<div class="endpoint">POST /signup</div>



Request:



<div class="code">

{

&#x20; "username": "user",

&#x20; "password": "password"

}

</div>



Response:



<div class="code">

{

&#x20; "message": "User created successfully"

}

</div>





<h3>Login utente</h3>



<div class="endpoint">POST /login</div>



Request:



<div class="code">

{

&#x20; "username": "user",

&#x20; "password": "password"

}

</div>



Response:



<div class="code">

{

&#x20; "access\_token": "JWT\_TOKEN",

&#x20; "token\_type": "bearer"

}

</div>



Header richiesto per richieste successive:



<div class="code">

Authorization: Bearer \&lt;JWT\_TOKEN\&gt;

</div>





<h2>Orchestrator API</h2>



Swagger UI:



<code>http://localhost:8001/docs</code>



Gestisce l’esecuzione asincrona delle pipeline MRI.





<h3>Upload immagine MRI</h3>



<div class="endpoint">POST /analyze/</div>



Descrizione:



Carica un file MRI in formato NIfTI e avvia la pipeline.



Request:



<div class="code">

multipart/form-data

file: .nii / .nii.gz

</div>



Response:



<div class="code">

{

&#x20; "task\_id": 1,

&#x20; "status": "PENDING"

}

</div>





<h3>Stato task pipeline</h3>



<div class="endpoint">GET /analyze/status/{task\_id}</div>



Response:



<div class="code">

{

&#x20; "task\_id": 1,

&#x20; "status": "RUNNING",

&#x20; "progress": 45

}

</div>



Possibili stati:



<ul>

<li>PENDING</li>

<li>RUNNING</li>

<li>COMPLETED</li>

<li>FAILED</li>

</ul>





<h3>Lista task utente</h3>



<div class="endpoint">GET /analyze/</div>



Response:



<div class="code">

\[

&#x20; {

&#x20;   "task\_id": 1,

&#x20;   "filename": "subject01.nii",

&#x20;   "status": "COMPLETED"

&#x20; }

]

</div>





<h2>Nextflow Worker API</h2>



Swagger UI:



<code>http://localhost:8005/docs</code>





<h3>Avvio preprocessing</h3>



<div class="endpoint">POST /start\_preprocessing</div>



Response:



<div class="code">

{

&#x20; "task\_id": 1,

&#x20; "status": "STARTED"

}

</div>





<h3>Stato preprocessing</h3>



<div class="endpoint">GET /status/{task\_id}</div>



Response:



<div class="code">

{

&#x20; "task\_id": 1,

&#x20; "status": "RUNNING"

}

</div>





<h2>Model Service API</h2>



Swagger UI:



<code>http://localhost:8003/docs</code>





<h3>Informazioni modello attivo</h3>



<div class="endpoint">GET /model\_info</div>



Response:



<div class="code">

{

&#x20; "model\_name": "HC\_vs\_bvFTD",

&#x20; "version": "latest"

}

</div>





<h3>Avvio inferenza diagnostica</h3>



<div class="endpoint">POST /predict</div>



Descrizione:



Invia dataset radiomico al motore di inferenza.



Response:



<div class="code">

{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82

}

</div>





<h2>Inference Engine API</h2>



Servizio basato su R + Plumber.



Endpoint principale:



<div class="endpoint">POST /infer</div>



Input:



dataset radiomico CSV



Output:



<div class="code">

{

&#x20; "prediction": "HC",

&#x20; "umap\_coordinates": \[1.25, -0.33, 2.11]

}

</div>





<h2>LLM Service API</h2>



Swagger UI:



<code>http://localhost:8002/docs</code>





<h3>Chat clinica</h3>



<div class="endpoint">POST /chat</div>



Request:



<div class="code">

{

&#x20; "message": "Interpret the diagnostic result"

}

</div>



Response:



<div class="code">

{

&#x20; "response": "The radiomic profile suggests compatibility with bvFTD."

}

</div>



Il servizio utilizza Spatial RAG per integrare informazioni radiomiche e embedding UMAP nella risposta.





<h2>Autenticazione API</h2>



Tutti gli endpoint protetti richiedono header:



<div class="code">

Authorization: Bearer \&lt;JWT\_TOKEN\&gt;

</div>



Il token viene ottenuto tramite login su api\_gateway.





<h2>Flusso API completo</h2>



Workflow tipico:



<div class="code">

Login → Upload MRI → Start preprocessing → Feature extraction → Classification → UMAP visualization → LLM interpretation

</div>



Questo flusso rappresenta la sequenza operativa standard della pipeline ClinicalTwin.

