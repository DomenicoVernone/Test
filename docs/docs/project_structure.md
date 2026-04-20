Struttura del progetto

Panoramica generale



Il progetto ClinicalTwin è organizzato secondo un’architettura modulare a microservizi containerizzati, in cui ogni componente applicativo è isolato in una directory dedicata e distribuito tramite Docker.



La struttura del repository riflette la separazione tra:



servizi backend

pipeline neuroimaging

motore statistico

assistente AI

frontend clinico

documentazione

configurazione del deployment



Questa organizzazione facilita la manutenzione del codice, l’estensione della piattaforma e la riproducibilità della pipeline radiomica.



Struttura ad alto livello



La struttura principale del repository è la seguente:



Tesi-FTD/

├── docker-compose.yml

├── .env.example

├── docs/

├── api\_gateway/

├── orchestrator/

├── model\_service/

├── inference\_engine/

├── llm\_service/

├── nextflow\_worker/

└── frontend/



Ogni directory rappresenta un microservizio indipendente del sistema ClinicalTwin.



docker-compose.yml



Il file:



docker-compose.yml



definisce l’orchestrazione dell’intero stack applicativo.



Specifica:



servizi containerizzati

porte esposte

volumi condivisi

dipendenze tra container

variabili d’ambiente



Questo file consente l’avvio completo della piattaforma tramite un singolo comando:



docker compose up --build

Directory docs/



La directory:



docs/



contiene la documentazione tecnica del progetto utilizzata da Read the Docs.



Include:



descrizione architettura

pipeline neuroimaging

configurazione dataset

installazione

testing

API REST



Questa documentazione supporta sia utenti clinici sia sviluppatori.



api\_gateway/



La directory:



api\_gateway/



implementa il servizio di autenticazione basato su FastAPI e token JWT.



Struttura:



api\_gateway/

├── main.py

├── core/

├── models/

└── routers/



Responsabilità principali:



registrazione utenti

autenticazione login

generazione token JWT

protezione accesso API



Costituisce il punto di ingresso sicuro alla piattaforma.



orchestrator/



La directory:



orchestrator/



contiene il servizio responsabile del coordinamento della pipeline neuroimaging.



Struttura:



orchestrator/

├── main.py

├── core/

├── models/

├── routers/

└── services/



Responsabilità principali:



gestione task MRI

monitoraggio stato elaborazioni

comunicazione con nextflow\_worker

invocazione model\_service

restituzione risultati al frontend



Questo servizio rappresenta il nodo centrale del workflow applicativo.



model\_service/



La directory:



model\_service/



gestisce l’integrazione con MLflow Model Registry tramite DagsHub.



Struttura:



model\_service/

├── main.py

├── core/

└── services/



Responsabilità principali:



recupero modello champion

versionamento modelli

gestione inferenza radiomica

interfacciamento con inference\_engine



Consente aggiornamenti dinamici del classificatore senza modificare la pipeline.



inference\_engine/



La directory:



inference\_engine/



implementa il motore statistico della piattaforma in linguaggio R tramite framework Plumber.



Struttura:



inference\_engine/

├── api.R

└── R/



Responsabilità principali:



classificazione KNN

calcolo embedding UMAP 3D

restituzione coordinate spazio latente

integrazione con model\_service



Questo modulo esegue la fase decisionale della pipeline diagnostica.



llm\_service/



La directory:



llm\_service/



implementa l’assistente clinico context-aware basato su modelli linguistici.



Struttura:



llm\_service/

├── main.py

├── core/

├── routers/

└── services/



Responsabilità principali:



interpretazione risultati diagnostici

supporto decisionale assistito

integrazione Spatial RAG

gestione memoria conversazionale multi-turno



Fornisce spiegazioni contestualizzate delle predizioni radiomiche.



nextflow\_worker/



La directory:



nextflow\_worker/



contiene la pipeline automatizzata di preprocessing neuroimaging.



Struttura:



nextflow\_worker/

├── main.py

├── nextflow/

├── data/

├── freesurfer.dockerfile

├── fsl.dockerfile

└── pyradiomics.dockerfile



Responsabilità principali:



segmentazione anatomica (FreeSurfer / FastSurfer)

generazione ROI cerebrali

estrazione feature radiomiche

generazione dataset CSV



Utilizza il paradigma Docker-out-of-Docker (DooD) per l’esecuzione dei container pipeline.



frontend/



La directory:



frontend/



contiene l’interfaccia utente clinica sviluppata con React e Vite.



Struttura:



frontend/

├── src/

├── components/

├── pages/

├── services/

└── contexts/



Responsabilità principali:



upload immagini MRI

monitoraggio pipeline

visualizzazione UMAP 3D

rendering volumetrico MRI tramite NiiVue

interazione con assistente AI



Costituisce il punto di accesso principale per l’utente finale.



Flusso operativo tra moduli



Il workflow completo del sistema segue la sequenza:



Frontend

→ API Gateway

→ Orchestrator

→ Nextflow Worker

→ Model Service

→ Inference Engine

→ Dashboard visualization

→ LLM Assistant



Questa struttura garantisce separazione funzionale tra acquisizione dati, preprocessing radiomico, inferenza statistica e supporto interpretativo clinico.

