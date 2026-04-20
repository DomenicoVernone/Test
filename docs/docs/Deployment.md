<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">

<title>Clinical Twin – Deployment</title>



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



.sidebar h2 { margin-top: 0; }



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

}



h2 {

&#x20;   margin-top: 40px;

&#x20;   font-size: 26px;

}



/\* ===== BLOCK ===== \*/



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

<li>API Reference</li>

<li class="active">Deployment</li>

</ul>



</div>





<div class="content">



<div class="breadcrumb">

Docs » Deployment

</div>



<h1>Deployment</h1>



<p>

Clinical Twin è progettato per essere eseguito in diversi ambienti di

deployment, dal computer locale fino a server GPU dedicati per pipeline

neuroimaging accelerate.

</p>





<h2>Deployment locale (Docker Desktop)</h2>



<div class="service-box">



<p>

Configurazione consigliata per sviluppo e test.

Compatibile con:

</p>



<ul>

<li>Windows (WSL2)</li>

<li>macOS</li>

<li>Linux</li>

</ul>



Avvio stack:



<div class="codeblock">

docker compose up -d --build

</div>



Accesso dashboard:



<div class="codeblock">

http://localhost:5173

</div>



</div>





<h2>Deployment su server Linux</h2>



<div class="service-box">



<p>

Configurazione consigliata per ambienti di ricerca o laboratorio.

Richiede:

</p>



<ul>

<li>Docker Engine</li>

<li>Docker Compose</li>

<li>CPU multicore</li>

<li>≥16GB RAM consigliati</li>

</ul>



Configurare volume condiviso:



<div class="codeblock">

HOST\_SHARED\_VOLUME\_DIR=/mnt/shared\_volume

</div>



Avvio servizi:



<div class="codeblock">

docker compose up -d

</div>



</div>





<h2>Deployment con GPU NVIDIA</h2>



<div class="service-box">



<p>

FastSurfer può utilizzare accelerazione CUDA per ridurre drasticamente

i tempi di segmentazione MRI.

</p>



Prerequisiti:



<ul>

<li>NVIDIA Driver aggiornati</li>

<li>CUDA Toolkit</li>

<li>NVIDIA Container Toolkit</li>

</ul>



Verifica GPU:



<div class="codeblock">

nvidia-smi

</div>



Configurazione device:



<div class="codeblock">

params.fastsurfer\_device=cuda

</div>



</div>





<h2>Deployment con GPU MIG (Multi-Instance GPU)</h2>



<div class="service-box">



<p>

Su server con GPU partizionata è possibile assegnare una singola MIG instance

alla pipeline Clinical Twin.

</p>



Configurare variabile:



<div class="codeblock">

MIG\_DEVICE=MIG-xxxxxxxxxxxxxxxx

</div>



Lasciare vuoto su GPU standard.



</div>





<h2>Deployment pipeline Nextflow</h2>



<div class="service-box">



<p>

Clinical Twin utilizza il modello Docker-out-of-Docker (DooD).

Le immagini della pipeline devono essere disponibili nel registry locale.

</p>



Build immagini:



<div class="codeblock">

docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/



docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/



docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

</div>



</div>





<h2>Deployment produzione (consigliato)</h2>



<div class="service-box">



Configurazione suggerita:



<ul>

<li>Server Linux dedicato</li>

<li>GPU NVIDIA</li>

<li>Docker Engine</li>

<li>Volume condiviso persistente</li>

<li>Backup dataset radiomico</li>

</ul>



Architettura supportata:



<div class="codeblock">

Frontend → API Gateway → Orchestrator → Nextflow Worker → Inference Engine → LLM Service

</div>



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

