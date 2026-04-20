<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Clinical Twin – Quickstart</title>

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

.sidebar h2 {
    margin-top: 0;
}

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

<!-- ===== SIDEBAR ===== -->

<div class="sidebar">

<h2>🏠 Clinical Twin</h2>

<input placeholder="Search docs">

<ul>
<li>Introduction</li>
<li>Installation</li>
<li class="active">Quickstart</li>
<li>User Guide</li>
</ul>

</div>


<!-- ===== MAIN CONTENT ===== -->

<div class="content">

<div class="breadcrumb">
Docs » Quickstart
</div>

<h1>Quickstart</h1>

<p>
Questa guida rapida mostra come eseguire la prima analisi di una risonanza
magnetica cerebrale utilizzando Clinical Twin dopo l’installazione dello stack.
</p>


<h2>1. Avvia lo stack Docker</h2>

<div class="codeblock">
docker compose up -d --build
</div>

<p>
Attendere il completamento dell’avvio dei microservizi prima di procedere.
</p>


<h2>2. Accedi alla dashboard</h2>

<p>
Aprire il browser all’indirizzo:
</p>

<div class="codeblock">
http://localhost:5173
</div>


<h2>3. Crea il primo utente</h2>

<p>
Se è il primo avvio del sistema, creare un utente tramite Swagger UI:
</p>

<div class="codeblock">
http://localhost:8000/docs
</div>

<p>
Eseguire la richiesta:
</p>

<div class="codeblock">
POST /signup
</div>


<h2>4. Carica una risonanza magnetica</h2>

<p>
Dopo il login nella dashboard:
</p>

<ul>
<li>aprire la sezione upload</li>
<li>selezionare un file MRI formato .nii oppure .nii.gz</li>
<li>avviare l’analisi</li>
</ul>


<h2>5. Avvia la pipeline di segmentazione</h2>

<p>
Il sistema eseguirà automaticamente:
</p>

<ul>
<li>preprocessing MRI</li>
<li>segmentazione cerebrale (FreeSurfer o FastSurfer)</li>
<li>estrazione feature radiomiche</li>
<li>inferenza statistica KNN</li>
<li>proiezione nello spazio latente UMAP</li>
</ul>


<h2>6. Visualizza i risultati</h2>

<p>
Al termine dell’elaborazione saranno disponibili:
</p>

<ul>
<li>segmentazione delle ROI cerebrali</li>
<li>coordinate nello spazio latente UMAP</li>
<li>classe diagnostica stimata</li>
<li>nearest neighbors clinici</li>
<li>spiegazione tramite assistente AI</li>
</ul>


<h2>7. Interroga l’assistente AI</h2>

<p>
Utilizzare il pannello laterale dell’assistente per:
</p>

<ul>
<li>interpretare i risultati radiomici</li>
<li>analizzare la posizione nello spazio UMAP</li>
<li>ottenere supporto diagnostico contestuale</li>
</ul>


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