<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">

<title>Clinical Twin – Microservices Overview</title>



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

<li class="active">Microservices Overview</li>

</ul>



</div>





<!-- ===== MAIN CONTENT ===== -->



<div class="content">



<div class="breadcrumb">

Docs » Microservices Overview

</div>



<h1>Microservices Overview</h1>



<p>

Clinical Twin è progettato secondo un’architettura a microservizi

containerizzati orchestrati tramite Docker Compose. Ogni servizio è

responsabile di uno specifico componente della pipeline neuroimaging

e comunica tramite API REST.

</p>





<h2>Panoramica dello stack</h2>



<div class="codeblock">

api\_gateway → orchestrator → nextflow\_worker → model\_service → inference\_engine → frontend

&#x20;                                    ↓

&#x20;                              llm\_service

</div>







<div class="service-box">



<h2>api\_gateway</h2>



<p>

Gestisce autenticazione utenti e sicurezza delle richieste tramite JWT.

Rappresenta il punto di ingresso principale per l’interazione con il sistema.

</p>



<ul>

<li>registrazione utenti</li>

<li>login autenticato</li>

<li>gestione token JWT</li>

<li>routing verso servizi backend</li>

</ul>



</div>







<div class="service-box">



<h2>orchestrator</h2>



<p>

Coordina l’esecuzione della pipeline radiomica gestendo task asincroni

e comunicazione tra servizi computazionali.

</p>



<ul>

<li>creazione task di analisi</li>

<li>monitoraggio stato pipeline</li>

<li>invocazione Nextflow</li>

<li>gestione workflow MRI</li>

</ul>



</div>







<div class="service-box">



<h2>nextflow\_worker</h2>



<p>

Esegue la pipeline neuroimaging strutturale utilizzando Nextflow e container

Docker dedicati.

</p>



<ul>

<li>preprocessing MRI</li>

<li>segmentazione FreeSurfer / FastSurfer</li>

<li>estrazione ROI cerebrali</li>

<li>estrazione feature radiomiche</li>

</ul>



</div>







<div class="service-box">



<h2>model\_service</h2>



<p>

Gestisce l’accesso ai modelli salvati su MLflow Model Registry ospitato su

DagsHub e prepara l’inferenza diagnostica.

</p>



<ul>

<li>download champion model</li>

<li>versioning modelli</li>

<li>integrazione MLflow</li>

<li>trigger inferenza</li>

</ul>



</div>







<div class="service-box">



<h2>inference\_engine</h2>



<p>

Implementato in R tramite Plumber, esegue classificazione KNN e proiezione

UMAP nello spazio latente diagnostico.

</p>



<ul>

<li>classificazione paziente</li>

<li>calcolo similarità clinica</li>

<li>embedding UMAP 3D</li>

<li>identificazione nearest neighbors</li>

</ul>



</div>







<div class="service-box">



<h2>llm\_service</h2>



<p>

Fornisce un assistente AI context-aware basato su Spatial RAG per supportare

l’interpretazione clinica dei risultati radiomici.

</p>



<ul>

<li>explainability radiomica</li>

<li>analisi cluster UMAP</li>

<li>memoria conversazionale multi-turno</li>

<li>integrazione Groq API</li>

</ul>



</div>







<div class="service-box">



<h2>frontend</h2>



<p>

Dashboard clinica sviluppata in React per l’interazione con il sistema

e la visualizzazione dei risultati.

</p>



<ul>

<li>upload MRI</li>

<li>viewer multiplanare NiiVue</li>

<li>visualizzazione spazio UMAP</li>

<li>storico analisi</li>

<li>assistente AI integrato</li>

</ul>



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

