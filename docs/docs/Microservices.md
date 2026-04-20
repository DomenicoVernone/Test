<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">

<title>Clinical Twin – Microservices Overview</title>



<style>



/\* ===== GLOBAL ===== \*/



body {

   margin: 0;

   font-family: "Segoe UI", Roboto, Arial, sans-serif;

   display: flex;

   background: #f5f6f7;

}



/\* ===== SIDEBAR ===== \*/



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



/\* ===== CONTENT ===== \*/



.content {

   margin-left: 0px;

   padding: 40px;

   max-width: 900px;

}



/\* ===== BREADCRUMB ===== \*/



.breadcrumb {

   color: #6c6c6c;

   font-size: 14px;

   margin-bottom: 10px;

}



/\* ===== HEADINGS ===== \*/



h1 {

   font-size: 36px;

   margin-bottom: 25px;

}



h2 {

   margin-top: 40px;

   font-size: 26px;

}



/\* ===== SERVICE BLOCK ===== \*/



.service-box {

   background: white;

   padding: 18px;

   border-radius: 8px;

   margin-top: 20px;

   box-shadow: 0px 2px 6px rgba(0,0,0,0.08);

}



/\* ===== CODE BLOCK ===== \*/



.codeblock {

   background: #eeeeee;

   padding: 14px;

   border-radius: 6px;

   font-family: monospace;

   margin: 15px 0;

}



/\* ===== NAV BUTTONS ===== \*/



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



/\* ===== FOOTER ===== \*/



.footer {

   margin-top: 50px;

   font-size: 14px;

   color: gray;

}



</style>

</head>



<body>



<!-- ===== SIDEBAR ===== -->





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

                                    ↓

                              llm\_service

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

