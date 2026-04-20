<style>

.install-box {

&#x20; border-left: 6px solid #3f51b5;

&#x20; background: #eef2ff;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}



.code {

&#x20; background: #f4f4f4;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; font-family: monospace;

&#x20; white-space: pre;

&#x20; overflow-x: auto;

}



.section {

&#x20; margin-top: 28px;

}

</style>





<h1>Installazione</h1>





<div class="install-box">



Questa sezione descrive la procedura completa per installare ed eseguire ClinicalTwin in ambiente locale utilizzando Docker Compose. Al termine della procedura sarà disponibile un’istanza funzionante della piattaforma con pipeline neuroimaging automatizzata e dashboard clinica interattiva.



</div>





<h2>Prerequisiti</h2>



Prima dell’installazione assicurarsi che siano disponibili i seguenti componenti:



<ul>

<li>Docker</li>

<li>Docker Compose</li>

<li>Git</li>

</ul>



Verifica installazione:



<div class="code">

docker --version

docker compose version

git --version

</div>





<h3>Requisiti opzionali</h3>



<ul>

<li>GPU NVIDIA (necessaria solo per FastSurfer)</li>

<li>WSL2 con supporto CUDA (solo Windows + GPU)</li>

</ul>



In assenza di GPU il sistema utilizza automaticamente FreeSurfer CPU.





<h2>Licenza FreeSurfer</h2>



Scaricare gratuitamente la licenza da:



https://surfer.nmr.mgh.harvard.edu/registration.html



e copiarla in:



<div class="code">

nextflow\_worker/license.txt

</div>





<h2>Clonazione repository</h2>



Scaricare il progetto:



<div class="code">

git clone https://github.com/DomenicoVernone/Test.git

cd Test

</div>





<h2>Configurazione variabili ambiente</h2>



Ogni microservizio utilizza un file <code>.env</code>.



Creare i file di configurazione:



<div class="code">

cp .env.example .env

cp api\_gateway/.env.example api\_gateway/.env

cp orchestrator/.env.example orchestrator/.env

cp model\_service/.env.example model\_service/.env

cp llm\_service/.env.example llm\_service/.env

cp frontend/.env.example frontend/.env

</div>





Configurare le variabili principali:



<ul>

<li><strong>SECRET\_KEY</strong> — chiave JWT condivisa tra api\_gateway, orchestrator, llm\_service</li>

<li><strong>GROQ\_API\_KEY</strong> — API key Groq</li>

<li><strong>MLFLOW\_TRACKING\_URI</strong> — URL MLflow su DagsHub</li>

<li><strong>MLFLOW\_TRACKING\_USERNAME</strong> — username DagsHub</li>

<li><strong>DAGSHUB\_TOKEN</strong> — token DagsHub</li>

<li><strong>REPO\_OWNER</strong> — proprietario repository</li>

<li><strong>REPO\_NAME</strong> — nome repository</li>

</ul>





<h2>Configurazione dataset pipeline</h2>



La pipeline Nextflow richiede file statici non inclusi nel repository.



Creare la struttura:



<div class="code">

nextflow\_worker/data/

└── external/

&#x20;   ├── ROI\_labels.tsv

&#x20;   └── pyradiomics.yaml

</div>



Questi file contengono:



<ul>

<li>etichette delle 78 ROI cerebrali</li>

<li>parametri di estrazione radiomica PyRadiomics</li>

</ul>



Senza questi file la pipeline non può essere eseguita.





<h2>Build immagini pipeline</h2>



La pipeline utilizza Docker-out-of-Docker (DooD). Le immagini devono essere costruite sull’host prima dell’avvio dello stack.



Eseguire:



<div class="code">

docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/

docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/

docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

</div>



Questo passaggio è necessario solo al primo avvio o dopo modifiche ai Dockerfile.





<h2>Avvio sistema</h2>



Avviare tutti i microservizi:



<div class="code">

docker compose up -d --build

</div>



Servizi avviati automaticamente:



<ul>

<li>api\_gateway</li>

<li>orchestrator</li>

<li>nextflow\_worker</li>

<li>model\_service</li>

<li>inference\_engine</li>

<li>llm\_service</li>

<li>frontend</li>

</ul>





<h2>Accesso alla dashboard</h2>



Aprire il browser:



<div class="code">

http://localhost:5173

</div>





Interfacce disponibili:



<ul>

<li>Frontend — http://localhost:5173</li>

<li>Swagger API Gateway — http://localhost:8000/docs</li>

<li>Swagger Orchestrator — http://localhost:8001/docs</li>

</ul>





<h2>Creazione primo utente</h2>



La registrazione non è disponibile tramite interfaccia grafica.



Creare un utente tramite Swagger:



<div class="code">

http://localhost:8000/docs

</div>



Eseguire endpoint:



<div class="code">

POST /signup

</div>



Inserendo:



<ul>

<li>username</li>

<li>password</li>

</ul>



Dopo la registrazione sarà possibile accedere alla dashboard.





<h2>Verifica installazione</h2>



Per verificare il corretto funzionamento del sistema:



<ul>

<li>accedere alla dashboard</li>

<li>caricare una MRI in formato NIfTI</li>

<li>avviare la pipeline</li>

<li>controllare lo stato elaborazione</li>

<li>visualizzare embedding UMAP</li>

</ul>



Frontend disponibile su:



<strong>http://localhost:5173</strong>



Se tutti i servizi risultano attivi, l’installazione è completata correttamente.

