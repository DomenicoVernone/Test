<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">

<title>Clinical Twin – Configuration</title>



<style>



/\* ===== GLOBAL ===== \*/



body {

&#x20;   margin: 0;

&#x20;   font-family: "Segoe UI", Roboto, Arial, sans-serif;

&#x20;   display: flex;

&#x20;   background: #f5f6f7;

}



/\* ===== SIDEBAR ===== \*/



.sidebar {

&#x20;   width: 300px;

&#x20;   height: 100vh;

&#x20;   background: linear-gradient(#2f6f95, #244f6a);

&#x20;   color: white;

&#x20;   position: fixed;

&#x20;   padding: 20px;

&#x20;   box-sizing: border-box;

}



.sidebar h2 {

&#x20;   margin-top: 0;

}



.sidebar input {

&#x20;   width: 100%;

&#x20;   padding: 8px;

&#x20;   border-radius: 6px;

&#x20;   border: none;

&#x20;   margin: 15px 0;

}



.sidebar ul {

&#x20;   list-style: none;

&#x20;   padding-left: 0;

}



.sidebar li {

&#x20;   padding: 6px 0;

&#x20;   opacity: 0.9;

}



.sidebar li.active {

&#x20;   font-weight: bold;

}



/\* ===== CONTENT ===== \*/



.content {

&#x20;   margin-left: 320px;

&#x20;   padding: 40px;

&#x20;   max-width: 900px;

}



/\* ===== BREADCRUMB ===== \*/



.breadcrumb {

&#x20;   color: #6c6c6c;

&#x20;   font-size: 14px;

&#x20;   margin-bottom: 10px;

}



/\* ===== HEADINGS ===== \*/



h1 {

&#x20;   font-size: 36px;

&#x20;   margin-bottom: 25px;

}



h2 {

&#x20;   margin-top: 40px;

&#x20;   font-size: 26px;

}



/\* ===== SERVICE BLOCK ===== \*/



.service-box {

&#x20;   background: white;

&#x20;   padding: 18px;

&#x20;   border-radius: 8px;

&#x20;   margin-top: 20px;

&#x20;   box-shadow: 0px 2px 6px rgba(0,0,0,0.08);

}



/\* ===== CODE BLOCK ===== \*/



.codeblock {

&#x20;   background: #eeeeee;

&#x20;   padding: 14px;

&#x20;   border-radius: 6px;

&#x20;   font-family: monospace;

&#x20;   margin: 15px 0;

}



/\* ===== TABLE ===== \*/



table {

&#x20;   border-collapse: collapse;

&#x20;   width: 100%;

&#x20;   margin-top: 15px;

}



th, td {

&#x20;   border: 1px solid #ddd;

&#x20;   padding: 10px;

}



th {

&#x20;   background: #f0f0f0;

}



/\* ===== NAV BUTTONS ===== \*/



.nav-buttons {

&#x20;   margin-top: 40px;

&#x20;   display: flex;

&#x20;   justify-content: space-between;

}



.button {

&#x20;   background: #e0e0e0;

&#x20;   border-radius: 6px;

&#x20;   padding: 10px 15px;

&#x20;   text-decoration: none;

&#x20;   color: black;

}



/\* ===== FOOTER ===== \*/



.footer {

&#x20;   margin-top: 50px;

&#x20;   font-size: 14px;

&#x20;   color: gray;

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

<li>Quickstart</li>

<li>System Architecture</li>

<li>Pipeline Workflow</li>

<li>Microservices Overview</li>

<li class="active">Configuration</li>

</ul>



</div>





<!-- ===== MAIN CONTENT ===== -->



<div class="content">



<div class="breadcrumb">

Docs » Configuration

</div>



<h1>Configuration</h1>



<p>

Clinical Twin utilizza file di configurazione distribuiti tra i vari

microservizi per gestire autenticazione, pipeline neuroimaging,

inferenza diagnostica e integrazione con servizi esterni.

</p>





<h2>File .env principali</h2>



<div class="codeblock">

.env

api\_gateway/.env

orchestrator/.env

model\_service/.env

llm\_service/.env

frontend/.env

</div>



<p>

Ogni servizio possiede un file di configurazione dedicato.

</p>





<h2>Variabili condivise (JWT)</h2>



<div class="service-box">



<table>

<tr>

<th>Variabile</th>

<th>Servizi</th>

<th>Descrizione</th>

</tr>



<tr>

<td>SECRET\_KEY</td>

<td>api\_gateway, orchestrator, llm\_service</td>

<td>Chiave condivisa per autenticazione JWT</td>

</tr>



</table>



</div>





<h2>Configurazione MLflow / DagsHub</h2>



<div class="service-box">



<table>

<tr>

<th>Variabile</th>

<th>Descrizione</th>

</tr>



<tr>

<td>MLFLOW\_TRACKING\_URI</td>

<td>URL tracking server MLflow</td>

</tr>



<tr>

<td>MLFLOW\_TRACKING\_USERNAME</td>

<td>Username DagsHub</td>

</tr>



<tr>

<td>DAGSHUB\_TOKEN</td>

<td>Token accesso Model Registry</td>

</tr>



<tr>

<td>REPO\_OWNER</td>

<td>Owner repository DagsHub</td>

</tr>



<tr>

<td>REPO\_NAME</td>

<td>Nome repository MLflow</td>

</tr>



</table>



</div>





<h2>Configurazione assistente AI</h2>



<div class="service-box">



<table>

<tr>

<th>Variabile</th>

<th>Descrizione</th>

</tr>



<tr>

<td>GROQ\_API\_KEY</td>

<td>Chiave API per accesso al modello LLM</td>

</tr>



</table>



</div>





<h2>Configurazione GPU (opzionale)</h2>



<p>

Se disponibile una GPU NVIDIA, FastSurfer può utilizzare accelerazione CUDA.

</p>



<div class="codeblock">

MIG\_DEVICE=

</div>



<p>

Su GPU partizionate impostare l’UUID della MIG instance.

Lasciare vuoto su sistemi CPU-only o GPU standard.

</p>





<h2>Configurazione volumi condivisi</h2>



<div class="codeblock">

HOST\_SHARED\_VOLUME\_DIR=

</div>



<p>

Parametro richiesto solo su sistemi Linux bare-metal.

Su Docker Desktop (Windows/macOS) può rimanere vuoto.

</p>





<h2>Configurazione pipeline Nextflow</h2>



<p>

I parametri principali della pipeline sono definiti in:

</p>



<div class="codeblock">

nextflow\_worker/nextflow/configs/nextflow.config

</div>





<div class="service-box">



<table>

<tr>

<th>Parametro</th>

<th>Descrizione</th>

</tr>



<tr>

<td>params.maxforks</td>

<td>Numero massimo processi paralleli</td>

</tr>



<tr>

<td>params.fastsurfer\_threads</td>

<td>Thread CPU FastSurfer</td>

</tr>



<tr>

<td>params.fastsurfer\_device</td>

<td>cpu oppure cuda</td>

</tr>



<tr>

<td>params.pyradiomics\_jobs</td>

<td>Numero job radiomica paralleli</td>

</tr>



<tr>

<td>params.brain\_segmenter</td>

<td>freesurfer oppure fastsurfer</td>

</tr>



</table>



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

