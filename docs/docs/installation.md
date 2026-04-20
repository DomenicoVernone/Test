Installazione



Questa sezione descrive la procedura completa per installare ed eseguire ClinicalTwin in ambiente locale utilizzando Docker Compose. Al termine della procedura sarà disponibile un’istanza funzionante della piattaforma con pipeline neuroimaging automatizzata e dashboard clinica interattiva.



Requisiti



Prima dell’installazione assicurarsi che siano disponibili i seguenti componenti:



Requisiti software

Docker

Docker Compose

Git



Verifica installazione:



docker --version

docker compose version

git --version

Requisiti opzionali

GPU NVIDIA (necessaria solo per FastSurfer)

WSL2 con supporto CUDA (solo Windows + GPU)



In assenza di GPU il sistema utilizza automaticamente FreeSurfer CPU.



Licenza FreeSurfer



Scaricare gratuitamente la licenza da:



https://surfer.nmr.mgh.harvard.edu/registration.html



e copiarla in:



nextflow\_worker/license.txt

Clonazione del repository



Scaricare il progetto:



git clone https://github.com/DomenicoVernone/Test.git

cd Test

Configurazione variabili d’ambiente



Ogni microservizio utilizza un file .env.



Creare i file di configurazione:



cp .env.example .env

cp api\_gateway/.env.example api\_gateway/.env

cp orchestrator/.env.example orchestrator/.env

cp model\_service/.env.example model\_service/.env

cp llm\_service/.env.example llm\_service/.env

cp frontend/.env.example frontend/.env



Configurare le variabili principali:



Variabile	Servizio	Descrizione

SECRET\_KEY	api\_gateway, orchestrator, llm\_service	Chiave JWT condivisa

GROQ\_API\_KEY	llm\_service	API key Groq

MLFLOW\_TRACKING\_URI	model\_service	URL MLflow su DagsHub

MLFLOW\_TRACKING\_USERNAME	model\_service	Username DagsHub

DAGSHUB\_TOKEN	model\_service	Token DagsHub

REPO\_OWNER	model\_service	Proprietario repository

REPO\_NAME	model\_service	Nome repository

Configurazione dataset pipeline



La pipeline Nextflow richiede file statici non inclusi nel repository.



Creare la struttura:



nextflow\_worker/data/

└── external/

&#x20;   ├── ROI\_labels.tsv

&#x20;   └── pyradiomics.yaml



Questi file contengono:



etichette delle 78 ROI cerebrali

parametri di estrazione radiomica PyRadiomics



Senza questi file la pipeline non può essere eseguita.



Build immagini Docker pipeline



La pipeline utilizza Docker-out-of-Docker (DooD). Le immagini devono essere costruite sull’host prima dell’avvio dello stack.



Eseguire:



docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/

docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/

docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/



Questo passaggio è necessario solo al primo avvio o dopo modifiche ai Dockerfile.



Avvio dello stack applicativo



Avviare tutti i microservizi:



docker compose up -d --build



Servizi avviati automaticamente:



api\_gateway

orchestrator

nextflow\_worker

model\_service

inference\_engine

llm\_service

frontend

Accesso alla dashboard



Aprire il browser:



http://localhost:5173



Interfacce disponibili:



Servizio	URL

Frontend	http://localhost:5173



Swagger API Gateway	http://localhost:8000/docs



Swagger Orchestrator	http://localhost:8001/docs

Creazione primo utente



La registrazione non è disponibile tramite interfaccia grafica.



Creare un utente tramite Swagger:



http://localhost:8000/docs



Eseguire endpoint:



POST /signup



Inserendo:



username

password



Dopo la registrazione sarà possibile accedere alla dashboard.



Verifica installazione



Per verificare il corretto funzionamento del sistema:



accedere alla dashboard

caricare una MRI in formato NIfTI

avviare la pipeline

controllare lo stato elaborazione

visualizzare embedding UMAP



Se tutti i servizi risultano attivi, l’installazione è completata correttamente. ✅

