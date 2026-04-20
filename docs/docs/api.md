<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Clinical Twin – API Reference</title>

<style>

/* ===== GLOBAL ===== */

body {
    margin: 0;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    display: flex;
    background: #f5f6f7;
}

/* ===== SIDEBAR ===== */

.sidebar {
    width: 300px;
    height: 100vh;
    background: linear-gradient(#2f6f95, #244f6a);
    color: white;
    position: fixed;
    padding: 20px;
    box-sizing: border-box;
}

.sidebar h2 { margin-top: 0; }

.sidebar input {
    width: 100%;
    padding: 8px;
    border-radius: 6px;
    border: none;
    margin: 15px 0;
}

.sidebar ul {
    list-style: none;
    padding-left: 0;
}

.sidebar li {
    padding: 6px 0;
    opacity: 0.9;
}

.sidebar li.active {
    font-weight: bold;
}

/* ===== CONTENT ===== */

.content {
    margin-left: 320px;
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

/* ===== SERVICE BLOCK ===== */

.endpoint-box {
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
}

/* ===== NAV BUTTONS ===== */

.nav-buttons {
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
}

.button {
    background: #e0e0e0;
    border-radius: 6px;
    padding: 10px 15px;
    text-decoration: none;
    color: black;
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

<div class="sidebar">

<h2>🏠 Clinical Twin</h2>

<input placeholder="Search docs">

<ul>
<li>Introduction</li>
<li>Installation</li>
<li>Quickstart</li>
<li>System Architecture</li>
<li>Pipeline Workflow</li>
<li>Microservices Overview</li>
<li>Configuration</li>
<li>Testing</li>
<li class="active">API Reference</li>
</ul>

</div>


<div class="content">

<div class="breadcrumb">
Docs » API Reference
</div>

<h1>API Reference</h1>

<p>
Clinical Twin espone una serie di endpoint REST tramite microservizi FastAPI
e Plumber (R). Questa sezione descrive le principali API disponibili per
autenticazione, gestione task, inferenza diagnostica e assistente AI.
</p>


<h2>api_gateway</h2>

<div class="endpoint-box">

<h3>POST /signup</h3>

<p>Crea un nuovo utente.</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

</div>


<div class="endpoint-box">

<h3>POST /login</h3>

<p>Autenticazione utente e generazione token JWT.</p>

<div class="codeblock">
{
  "username": "user",
  "password": "password"
}
</div>

</div>


<div class="endpoint-box">

<h3>GET /me</h3>

<p>Restituisce informazioni sull’utente autenticato.</p>

</div>


<h2>orchestrator</h2>

<div class="endpoint-box">

<h3>POST /analyze</h3>

<p>
Avvia una nuova pipeline di analisi radiomica su MRI caricata.
</p>

<div class="codeblock">
{
  "filename": "subject01.nii.gz"
}
</div>

</div>


<div class="endpoint-box">

<h3>GET /task/{task_id}</h3>

<p>
Restituisce lo stato corrente del task di analisi.
</p>

</div>


<div class="endpoint-box">

<h3>GET /tasks</h3>

<p>
Elenco delle analisi eseguite dall’utente.
</p>

</div>


<h2>model_service</h2>

<div class="endpoint-box">

<h3>POST /load-model</h3>

<p>
Scarica il champion model dal registry MLflow.
</p>

</div>


<div class="endpoint-box">

<h3>POST /predict</h3>

<p>
Invia feature radiomiche al motore di inferenza.
</p>

</div>


<h2>inference_engine</h2>

<div class="endpoint-box">

<h3>POST /knn</h3>

<p>
Restituisce la classificazione diagnostica basata su KNN.
</p>

Esempio risposta:

<div class="codeblock">
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</div>

</div>


<div class="endpoint-box">

<h3>POST /umap</h3>

<p>
Calcola la proiezione del paziente nello spazio latente UMAP.
</p>

</div>


<h2>llm_service</h2>

<div class="endpoint-box">

<h3>POST /chat</h3>

<p>
Invia una richiesta all’assistente AI context-aware.
</p>

<div class="codeblock">
{
  "message": "Explain this patient's cluster position"
}
</div>

</div>


<h2>Swagger UI</h2>

<p>
La documentazione completa e interattiva delle API è disponibile tramite Swagger:
</p>

<div class="codeblock">
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
</div>


<div class="nav-buttons">

<a class="button">⬅ Previous</a>
<a class="button">Next ➡</a>

</div>


<div class="footer">

© 2025 Clinical Twin Documentation  
Built with custom HTML/CSS (ReadTheDocs-style layout)

</div>

</div>

</body>
</html>