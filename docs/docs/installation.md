<style>

.install-box {

&#x20; border-left: 6px solid #3f51b5;

&#x20; background: #eef2ff;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

}

.code {

&#x20; background: #f4f4f4;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; font-family: monospace;

}

</style>



<h1>Installazione</h1>



<div class="install-box">

Questa sezione descrive l’installazione locale della piattaforma ClinicalTwin tramite Docker Compose.

</div>



<h2>Prerequisiti</h2>



<ul>

<li>Docker</li>

<li>Docker Compose</li>

<li>Git</li>

</ul>



<h2>Clonazione repository</h2>



<div class="code">

git clone https://github.com/DomenicoVernone/Test.git

cd Test

</div>



<h2>Configurazione variabili ambiente</h2>



<div class="code">

cp .env.example .env

</div>



Configurare:



<ul>

<li>SECRET\_KEY</li>

<li>GROQ\_API\_KEY</li>

<li>MLFLOW\_TRACKING\_URI</li>

</ul>



<h2>Build immagini pipeline</h2>



<div class="code">

docker build -t clinical-freesurfer ...

docker build -t clinical-fsl ...

docker build -t clinical-pyradiomics ...

</div>



<h2>Avvio sistema</h2>



<div class="code">

docker compose up -d --build

</div>



Frontend disponibile su:



<strong>http://localhost:5173</strong>

