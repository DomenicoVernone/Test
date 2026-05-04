<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – API Reference</title>

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

<h1>API REST – Sistema MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
Il sistema MLOps espone un insieme di API REST che consentono la comunicazione
tra microservizi e l’interazione con il frontend clinico.
</p>

<p>
Le API rappresentano il livello di integrazione dell’intera piattaforma e
definiscono il contratto tra:
</p>

<ul>
<li>utente e sistema (frontend → backend)</li>
<li>microservizi interni</li>
<li>pipeline e motore di inferenza</li>
</ul>

<p>
Gli endpoint sono implementati principalmente tramite FastAPI (Python)
e Plumber (R) e utilizzano JSON come formato standard per richieste e risposte.
</p>

</div>

<div class="section">
<h2>2. Architettura delle API</h2>

<p>
Le API seguono un modello distribuito in cui ogni microservizio espone
endpoint specifici per il proprio dominio funzionale.
</p>

<pre>
Frontend
   ↓
API Gateway (autenticazione)
   ↓
Orchestrator (task pipeline)
   ↓
Nextflow Worker (pipeline)
   ↓
Inference Engine (KNN + UMAP)
   ↓
LLM Service (explainability)
</pre>

<p>
L’API Gateway rappresenta il punto di ingresso principale e gestisce
l’autenticazione tramite token JWT.
</p>

</div>

<div class="section">
<h2>3. Autenticazione e sicurezza</h2>

<p>
Il sistema utilizza autenticazione basata su JSON Web Token (JWT)
per proteggere gli endpoint.
</p>

<p>
Flusso di autenticazione:
</p>

<pre>
1. Utente effettua login
2. Server genera JWT
3. Token incluso nelle richieste successive
4. Servizi validano il token
</pre>

<p>
Header richiesto:
</p>

<pre>
Authorization: Bearer &lt;token&gt;
</pre>

</div>

<div class="section">
<h2>4. API api_gateway</h2>

<h3>4.1 Registrazione utente</h3>

<pre>
POST /signup
</pre>

<p>Request:</p>

<pre>
{
  "username": "user",
  "password": "password"
}
</pre>

<p>Response:</p>

<pre>
{
  "message": "User created successfully"
}
</pre>

<h3>4.2 Login</h3>

<pre>
POST /login
</pre>

<p>Response:</p>

<pre>
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
</pre>

<h3>4.3 Informazioni utente</h3>

<pre>
GET /me
</pre>

<p>Response:</p>

<pre>
{
  "username": "user"
}
</pre>

</div>

<div class="section">
<h2>5. API orchestrator</h2>

<h3>5.1 Avvio analisi MRI</h3>

<pre>
POST /analyze
</pre>

<p>Request:</p>

<pre>
{
  "filename": "subject01.nii.gz"
}
</pre>

<p>Response:</p>

<pre>
{
  "task_id": "12345",
  "status": "pending"
}
</pre>

<h3>5.2 Stato task</h3>

<pre>
GET /task/{task_id}
</pre>

<p>Response:</p>

<pre>
{
  "task_id": "12345",
  "status": "running",
  "created_at": "timestamp"
}
</pre>

<h3>5.3 Lista task</h3>

<pre>
GET /tasks
</pre>

<p>
Restituisce tutte le analisi associate all’utente autenticato.
</p>

</div>

<div class="section">
<h2>6. API inference_engine</h2>

<h3>6.1 Classificazione KNN</h3>

<pre>
POST /knn
</pre>

<p>Response:</p>

<pre>
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</pre>

<h3>6.2 Proiezione UMAP</h3>

<pre>
POST /umap
</pre>

<p>Response:</p>

<pre>
{
  "x": 1.23,
  "y": -0.45,
  "z": 2.11
}
</pre>

</div>

<div class="section">
<h2>7. API model_service</h2>

<h3>7.1 Caricamento modello</h3>

<pre>
POST /load-model
</pre>

<p>
Scarica il modello dal Model Registry MLflow e lo rende disponibile
per l’inference_engine.
</p>

<h3>7.2 Predizione (opzionale)</h3>

<pre>
POST /predict
</pre>

<p>
Endpoint opzionale per inferenza diretta (non utilizzato nel flusso principale).
</p>

</div>

<div class="section">
<h2>8. API llm_service</h2>

<h3>8.1 Chat AI</h3>

<pre>
POST /chat
</pre>

<p>Request:</p>

<pre>
{
  "message": "Explain this patient's diagnosis"
}
</pre>

<p>Response:</p>

<pre>
{
  "response": "The patient is located near..."
}
</pre>

<p>
Questo endpoint utilizza feature radiomiche e coordinate UMAP
per generare spiegazioni cliniche contestualizzate.
</p>

</div>

<div class="section">
<h2>9. Contratto dati tra servizi</h2>

<p>
Le API definiscono un contratto dati chiaro tra i componenti del sistema.
</p>

<p>
Elemento centrale:
</p>

<pre>
radiomics_features.csv
</pre>

<p>
Questo file rappresenta l’input standard per l’inference_engine
e garantisce coerenza tra pipeline e inferenza.
</p>

<p>
Output inferenza:
</p>

<pre>
{
  "prediction": "...",
  "confidence": 0.XX,
  "umap_coordinates": [x, y, z]
}
</pre>

</div>

<div class="section">
<h2>10. Swagger e testing</h2>

<p>
Ogni microservizio FastAPI espone una documentazione interattiva
tramite Swagger UI:
</p>

<pre>
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
</pre>

<p>
Swagger consente:
</p>

<ul>
<li>test degli endpoint</li>
<li>validazione JSON</li>
<li>debug rapido</li>
</ul>

</div>

<div class="section">
<h2>11. Gestione errori</h2>

<p>
Le API seguono convenzioni standard HTTP:
</p>

<ul>
<li>200 → successo</li>
<li>401 → non autorizzato</li>
<li>404 → risorsa non trovata</li>
<li>500 → errore interno</li>
</ul>

<p>
Gli errori vengono propagati tra servizi per garantire consistenza
nel workflow.
</p>

</div>

<div class="section">
<h2>12. Conclusioni</h2>

<p>
Le API costituiscono il backbone di comunicazione del sistema MLOps,
garantendo interoperabilità tra microservizi e integrazione con il frontend.
</p>

<p>
La definizione chiara dei contratti dati e degli endpoint consente
un’evoluzione modulare del sistema e facilita lo sviluppo di nuove
funzionalità.
</p>

</div>

</div>

</body>
</html>
