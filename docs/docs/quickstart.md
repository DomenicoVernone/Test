<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">

<title>Clinical Twin – Quickstart</title>



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

