API Documentation

Panoramica generale



ClinicalTwin espone un insieme di REST API distribuite su più microservizi containerizzati. Le API consentono la gestione dell’autenticazione, l’avvio della pipeline neuroimaging, l’esecuzione dell’inferenza diagnostica e l’interazione con l’assistente clinico basato su modelli linguistici.



I servizi principali che espongono endpoint sono:



Servizio	Porta	Funzione

api\_gateway	8000	Autenticazione utenti

orchestrator	8001	Gestione task pipeline

llm\_service	8002	Assistente AI

model\_service	8003	Gestione modelli ML

inference\_engine	8004	Inferenza statistica

nextflow\_worker	8005	Pipeline neuroimaging



Le API sono documentate automaticamente tramite Swagger UI.



API Gateway



Swagger UI:



http://localhost:8000/docs



Gestisce autenticazione e generazione token JWT.



Registrazione utente



Endpoint:



POST /signup



Request:



{

&#x20; "username": "user",

&#x20; "password": "password"

}



Response:



{

&#x20; "message": "User created successfully"

}

Login utente



Endpoint:



POST /login



Request:



{

&#x20; "username": "user",

&#x20; "password": "password"

}



Response:



{

&#x20; "access\_token": "JWT\_TOKEN",

&#x20; "token\_type": "bearer"

}



Il token deve essere incluso negli header delle richieste successive:



Authorization: Bearer <JWT\_TOKEN>

Orchestrator API



Swagger UI:



http://localhost:8001/docs



Gestisce l’esecuzione asincrona delle pipeline MRI.



Upload immagine MRI



Endpoint:



POST /analyze/



Descrizione:



Carica un file MRI in formato NIfTI e avvia la pipeline.



Request:



multipart/form-data



Parametro:



Campo	Tipo	Descrizione

file	.nii / .nii.gz	MRI strutturale



Response:



{

&#x20; "task\_id": 1,

&#x20; "status": "PENDING"

}

Stato task pipeline



Endpoint:



GET /analyze/status/{task\_id}



Response:



{

&#x20; "task\_id": 1,

&#x20; "status": "RUNNING",

&#x20; "progress": 45

}



Possibili stati:



PENDING

RUNNING

COMPLETED

FAILED

Lista task utente



Endpoint:



GET /analyze/



Descrizione:



Restituisce lo storico delle elaborazioni effettuate.



Response:



\[

&#x20; {

&#x20;   "task\_id": 1,

&#x20;   "filename": "subject01.nii",

&#x20;   "status": "COMPLETED"

&#x20; }

]

Nextflow Worker API



Swagger UI:



http://localhost:8005/docs



Gestisce l’esecuzione della pipeline neuroimaging.



Avvio preprocessing



Endpoint:



POST /start\_preprocessing



Descrizione:



Avvia la pipeline Nextflow su un dataset MRI.



Response:



{

&#x20; "task\_id": 1,

&#x20; "status": "STARTED"

}

Stato preprocessing



Endpoint:



GET /status/{task\_id}



Response:



{

&#x20; "task\_id": 1,

&#x20; "status": "RUNNING"

}

Model Service API



Swagger UI:



http://localhost:8003/docs



Gestisce il recupero del modello champion tramite MLflow.



Informazioni modello attivo



Endpoint:



GET /model\_info



Response:



{

&#x20; "model\_name": "HC\_vs\_bvFTD",

&#x20; "version": "latest"

}

Avvio inferenza diagnostica



Endpoint:



POST /predict



Descrizione:



Invia dataset radiomico al motore di inferenza.



Response:



{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82

}

Inference Engine API



Servizio basato su R + Plumber



Endpoint principale:



POST /infer



Input:



dataset radiomico CSV



Output:



{

&#x20; "prediction": "HC",

&#x20; "umap\_coordinates": \[1.25, -0.33, 2.11]

}



Restituisce:



classe diagnostica

coordinate spazio latente UMAP

LLM Service API



Swagger UI:



http://localhost:8002/docs



Fornisce supporto interpretativo context-aware.



Chat clinica



Endpoint:



POST /chat



Request:



{

&#x20; "message": "Interpret the diagnostic result"

}



Response:



{

&#x20; "response": "The radiomic profile suggests compatibility with bvFTD."

}



Il servizio utilizza Spatial RAG per integrare informazioni radiomiche e embedding UMAP nella risposta.



Autenticazione API



Tutti gli endpoint protetti richiedono header:



Authorization: Bearer <JWT\_TOKEN>



Il token viene ottenuto tramite login su api\_gateway.



Flusso API completo



Workflow tipico:



Login → Upload MRI → Start preprocessing → Feature extraction → Classification → UMAP visualization → LLM interpretation



Questo flusso rappresenta la sequenza operativa standard della pipeline ClinicalTwin.

