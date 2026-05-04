<!DOCTYPE html>

<html lang="it">
<head>
<meta charset="UTF-8">
<title>MLOps – Components & Project Structure</title>

<style>body {
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

<h1>🧩 System Components & Project Structure</h1>

<div class="section">
<h2>1. Struttura repository</h2>

<pre>
Tesi-FTD/
├── api_gateway/
├── orchestrator/
├── model_service/
├── llm_service/
├── inference_engine/
├── nextflow_worker/
└── frontend/
</pre>

</div>

<div class="section">
<h2>2. Panoramica microservizi</h2>

<table>
<tr><th>Servizio</th><th>Ruolo</th></tr>

<tr><td>api_gateway</td><td>Autenticazione e sicurezza</td></tr>
<tr><td>orchestrator</td><td>Gestione workflow</td></tr>
<tr><td>nextflow_worker</td><td>Pipeline MRI</td></tr>
<tr><td>inference_engine</td><td>Inferenza ML</td></tr>
<tr><td>model_service</td><td>Gestione modelli</td></tr>
<tr><td>llm_service</td><td>Explainability AI</td></tr>
<tr><td>frontend</td><td>Interfaccia utente</td></tr>

</table>

</div>

<div class="section">
<h2>3. Descrizione servizi</h2>

<h3>api_gateway</h3>
<p>Gestisce autenticazione JWT e routing.</p>

<h3>orchestrator</h3>
<p>Coordina pipeline e stato task.</p>

<h3>nextflow_worker</h3>
<p>Esegue pipeline radiomica.</p>

<h3>inference_engine</h3>
<p>Esegue classificazione e UMAP.</p>

<h3>model_service</h3>
<p>Gestisce modelli MLflow.</p>

<h3>llm_service</h3>
<p>Explainability AI.</p>

<h3>frontend</h3>
<p>Dashboard React.</p>

</div>

<div class="section">
<h2>4. Comunicazione</h2>

<ul>
<li>REST API</li>
<li>volumi Docker</li>
</ul>

</div>

</div>

</body>
</html>
