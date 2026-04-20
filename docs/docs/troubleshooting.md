<style>

.warn {

&#x20; border-left: 6px solid #f44336;

&#x20; background: #fdecea;

&#x20; padding: 14px;

&#x20; margin: 18px 0;

&#x20; border-radius: 6px;

}



.code {

&#x20; font-family: monospace;

&#x20; background: #eeeeee;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; white-space: pre;

}

</style>





<h1>Troubleshooting</h1>





<div class="warn">



Questa sezione raccoglie i problemi più comuni riscontrabili durante l’installazione, l’avvio e l’utilizzo della piattaforma ClinicalTwin, insieme alle relative soluzioni operative.



Le problematiche più frequenti riguardano:



<ul>

<li>configurazione Docker</li>

<li>pipeline Nextflow</li>

<li>segmentazione FreeSurfer</li>

<li>connessione MLflow / DagsHub</li>

<li>licenza FreeSurfer</li>

<li>configurazione dataset radiomico</li>

<li>build documentazione Read the Docs</li>

</ul>



</div>





<h2>Docker non avviato</h2>



Errore tipico:



<div class="code">

Cannot connect to the Docker daemon

</div>



Soluzione:



Verificare che Docker Desktop sia avviato:



<div class="code">

docker info

</div>



Se il comando fallisce:



<ul>

<li>avviare Docker Desktop</li>

<li>verificare modalità Linux containers</li>

<li>riavviare Docker</li>

</ul>





<h2>Container terminano immediatamente</h2>



Verificare i log:



<div class="code">

docker compose logs -f

</div>



Oppure per un singolo servizio:



<div class="code">

docker compose logs orchestrator

</div>



Controllare:



<ul>

<li>variabili .env</li>

<li>porte occupate</li>

<li>file mancanti</li>

<li>credenziali MLflow</li>

</ul>





<h2>FreeSurfer license missing</h2>



Errore tipico:



<div class="code">

ERROR: FreeSurfer license file not found

</div>



Soluzione:



Scaricare la licenza da:



https://surfer.nmr.mgh.harvard.edu/registration.html



Inserire il file in:



<div class="code">

nextflow\_worker/license.txt

</div>



Ricostruire i container:



<div class="code">

docker compose up --build

</div>





<h2>Pipeline Nextflow bloccata</h2>



Errore tipico:



<div class="code">

process > freesurfer (1) \[0%]

</div>



Cause possibili:



<strong>1️⃣ immagini Docker pipeline non costruite</strong>



Eseguire:



<div class="code">

docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/



docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/



docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

</div>





<strong>2️⃣ file ROI\_labels.tsv mancante</strong>



Verificare presenza:



<div class="code">

nextflow\_worker/data/external/ROI\_labels.tsv

</div>





<strong>3️⃣ configurazione PyRadiomics assente</strong>



Verificare presenza:



<div class="code">

nextflow\_worker/data/external/pyradiomics.yaml

</div>





<h2>Nextflow non trova Docker host (errore DooD)</h2>



Errore tipico:



<div class="code">

Cannot connect to Docker daemon

</div>



La pipeline utilizza architettura Docker-out-of-Docker (DooD).



Verificare:



<div class="code">

docker ps

</div>



Se vuoto o errore → Docker non attivo.





<h2>Errore database orchestrator</h2>



Errore tipico:



<div class="code">

sqlite3.OperationalError: no such table: tasks

</div>



Soluzione:



Creare le tabelle database:



<div class="code">

docker compose exec orchestrator bash



python -c "from models.domain import Base; from core.database import engine; Base.metadata.create\_all(bind=engine)"

</div>



Riavviare il servizio:



<div class="code">

docker compose restart orchestrator

</div>





<h2>MLflow / DagsHub non connesso</h2>



Errore tipico:



<div class="code">

401 Unauthorized

</div>



Verificare variabili:



<ul>

<li>MLFLOW\_TRACKING\_URI</li>

<li>MLFLOW\_TRACKING\_USERNAME</li>

<li>DAGSHUB\_TOKEN</li>

<li>REPO\_OWNER</li>

<li>REPO\_NAME</li>

</ul>



Controllare:



<ul>

<li>token valido</li>

<li>repository esistente</li>

<li>permessi di accesso corretti</li>

</ul>





<h2>LLM service non risponde</h2>



Errore tipico:



<div class="code">

Groq API key missing

</div>



Soluzione:



Inserire nel file:



<div class="code">

llm\_service/.env

</div>



la variabile:



<div class="code">

GROQ\_API\_KEY=\&lt;your\_api\_key\&gt;

</div>



Riavviare il servizio:



<div class="code">

docker compose restart llm\_service

</div>





<h2>Frontend non accessibile</h2>



Verificare accesso:



http://localhost:5173



Se non disponibile:



<div class="code">

docker compose ps

</div>



oppure:



<div class="code">

docker compose logs frontend

</div>



Possibili cause:



<ul>

<li>porta occupata</li>

<li>errore build Vite</li>

<li>API backend non attive</li>

</ul>





<h2>Swagger UI non visibile</h2>



Endpoint disponibili:



<ul>

<li>http://localhost:8000/docs</li>

<li>http://localhost:8001/docs</li>

<li>http://localhost:8002/docs</li>

<li>http://localhost:8003/docs</li>

<li>http://localhost:8005/docs</li>

</ul>



Se non accessibili:



<div class="code">

docker compose ps

</div>





<h2>Build Read the Docs fallita</h2>



Errore tipico:



<div class="code">

Unrecognised theme name: material

</div>



Soluzione:



Aggiungere in:



<div class="code">

readthedocs.yaml

</div>



la sezione:



<div class="code">

python:

&#x20; install:

&#x20;   - requirements: docs/requirements.txt

</div>



Inserire nel file:



<div class="code">

docs/requirements.txt

</div>



la dipendenza:



<div class="code">

mkdocs-material

</div>





<h2>Dataset radiomico non generato</h2>



Errore tipico:



<div class="code">

radiomics\_features.csv not found

</div>



Verificare:



<ul>

<li>licenza FreeSurfer</li>

<li>immagini Docker pipeline</li>

<li>ROI\_labels.tsv</li>

<li>pyradiomics.yaml</li>

<li>file MRI valido (.nii oppure .nii.gz)</li>

</ul>





<h2>FastSurfer non utilizza GPU</h2>



FastSurfer richiede:



<ul>

<li>GPU NVIDIA</li>

<li>CUDA installato</li>

<li>WSL2 (Windows)</li>

</ul>



Verificare:



<div class="code">

nvidia-smi

</div>



Se non disponibile:



impostare nel file:



<div class="code">

nextflow\_worker/nextflow/configs/nextflow.config

</div>



il parametro:



<div class="code">

params.brain\_segmenter = freesurfer

</div>





<h2>Reset ambiente completo</h2>



Se la pipeline presenta errori persistenti:



<div class="code">

docker compose down -v

docker compose build --no-cache

docker compose up -d

</div>



Questo rimuove:



<ul>

<li>volumi</li>

<li>cache pipeline</li>

<li>database temporanei</li>

</ul>



e ripristina uno stato pulito del sistema.

