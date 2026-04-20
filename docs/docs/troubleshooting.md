Troubleshooting

Panoramica



Questa sezione raccoglie i problemi più comuni riscontrabili durante l’installazione, l’avvio e l’utilizzo della piattaforma ClinicalTwin, insieme alle relative soluzioni operative.



Le problematiche più frequenti riguardano:



configurazione Docker

pipeline Nextflow

segmentazione FreeSurfer

connessione MLflow / DagsHub

licenza FreeSurfer

configurazione dataset radiomico

build della documentazione Read the Docs

Problemi Docker

Docker non avvia i servizi



Errore tipico:



Cannot connect to the Docker daemon



Soluzione:



Verificare che Docker Desktop sia avviato:



docker info



Se il comando fallisce:



avviare Docker Desktop

verificare modalità Linux containers

riavviare Docker

Container terminano immediatamente



Verificare i log:



docker compose logs -f



Oppure per un singolo servizio:



docker compose logs orchestrator



Controllare:



variabili .env

porte occupate

file mancanti

credenziali MLflow

Errore FreeSurfer license missing



Errore tipico:



ERROR: FreeSurfer license file not found



Soluzione:



Scaricare la licenza da:



https://surfer.nmr.mgh.harvard.edu/registration.html



Copiarla in:



nextflow\_worker/license.txt



Poi ricostruire i container:



docker compose up --build

Pipeline Nextflow non parte



Errore tipico:



process > freesurfer (1) \[0%]



Cause possibili:



1️⃣ immagini Docker pipeline non costruite



Eseguire:



docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/

docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/

docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

2️⃣ file ROI\_labels.tsv mancante



Verificare presenza:



nextflow\_worker/data/external/ROI\_labels.tsv

3️⃣ configurazione PyRadiomics assente



Verificare presenza:



nextflow\_worker/data/external/pyradiomics.yaml

Nextflow non trova Docker host (errore DooD)



Errore tipico:



Cannot connect to Docker daemon



La pipeline utilizza architettura:



Docker-out-of-Docker (DooD)



Verificare:



docker ps



Se vuoto o errore → Docker non attivo.



Task orchestrator: errore "no such table: tasks"



Errore tipico:



sqlite3.OperationalError: no such table: tasks



Soluzione:



Creare le tabelle database:



docker compose exec orchestrator bash



poi:



python -c "from models.domain import Base; from core.database import engine; Base.metadata.create\_all(bind=engine)"



Riavviare il servizio:



docker compose restart orchestrator

MLflow / DagsHub non connesso



Errore tipico:



401 Unauthorized



Verificare variabili:



MLFLOW\_TRACKING\_URI

MLFLOW\_TRACKING\_USERNAME

DAGSHUB\_TOKEN

REPO\_OWNER

REPO\_NAME



Controllare:



token valido

repo esistente

permessi accesso

LLM service non risponde



Errore tipico:



Groq API key missing



Soluzione:



Inserire nel file:



llm\_service/.env



la variabile:



GROQ\_API\_KEY=<your\_api\_key>



Riavviare:



docker compose restart llm\_service

Frontend non accessibile



Controllare:



http://localhost:5173



Se non disponibile:



verificare container:



docker compose ps



oppure:



docker compose logs frontend



Possibili cause:



porta occupata

errore build Vite

API backend non attive

Swagger UI non visibile



Endpoint disponibili:



Servizio	URL

api\_gateway	http://localhost:8000/docs



orchestrator	http://localhost:8001/docs



llm\_service	http://localhost:8002/docs



model\_service	http://localhost:8003/docs



nextflow\_worker	http://localhost:8005/docs



Se non accessibili:



verificare container attivi:



docker compose ps

Build Read the Docs fallita



Errore tipico:



Unrecognised theme name: material



Soluzione:



aggiungere in:



readthedocs.yaml



la sezione:



python:

&#x20; install:

&#x20;   - requirements: docs/requirements.txt



e inserire nel file:



docs/requirements.txt



la dipendenza:



mkdocs-material

Dataset radiomico non generato



Errore tipico:



radiomics\_features.csv not found



Verificare:



licenza FreeSurfer

immagini Docker pipeline

ROI\_labels.tsv

pyradiomics.yaml

file MRI valido (.nii oppure .nii.gz)

FastSurfer non utilizza GPU



FastSurfer richiede:



GPU NVIDIA

CUDA installato

WSL2 (Windows)



Verificare:



nvidia-smi



Se non disponibile:



impostare nel file:



nextflow\_worker/nextflow/configs/nextflow.config



il parametro:



params.brain\_segmenter = freesurfer



per eseguire segmentazione su CPU.



Reset completo ambiente



Se la pipeline presenta errori persistenti:



eseguire reset completo:



docker compose down -v

docker compose build --no-cache

docker compose up -d



Questo rimuove:



volumi

cache pipeline

database temporanei ⚙️



e ripristina uno stato pulito del sistema.

