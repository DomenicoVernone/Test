Architettura del sistema

Panoramica generale dell’architettura



La piattaforma ClinicalTwin è progettata secondo un’architettura distribuita a microservizi containerizzati orchestrati tramite Docker Compose, con separazione funzionale tra componenti di autenticazione, orchestrazione pipeline, preprocessing neuroimaging, inferenza statistica e interfaccia utente.



L’obiettivo architetturale principale è garantire:



modularità del sistema;

scalabilità dei componenti computazionali;

riproducibilità delle pipeline neuroimaging;

separazione tra livelli applicativi;

interoperabilità tra servizi clinico-computazionali.



Ogni componente svolge un ruolo specifico all’interno della pipeline di analisi MRI per la classificazione diagnostica bvFTD vs Healthy Control 



Servizi Docker



L’intero sistema ClinicalTwin è distribuito come insieme di servizi containerizzati gestiti tramite Docker Compose, che consente l’esecuzione coordinata dei moduli applicativi.



I principali servizi includono:



API Gateway per autenticazione e gestione utenti;

Orchestrator per la gestione dei task asincroni;

Nextflow Worker per preprocessing neuroimaging;

Model Service per inferenza statistica;

LLM Service per assistenza clinica context-aware;

Frontend React per interazione utente.



Questa architettura consente l’isolamento delle dipendenze software e la replicabilità dell’ambiente computazionale su sistemi differenti.



Orchestrator



Il servizio orchestrator rappresenta il nodo centrale di coordinamento della pipeline di analisi.



È implementato come servizio backend basato su FastAPI e ha il compito di:



ricevere richieste di analisi MRI dal frontend;

registrare i task nel database applicativo;

gestire lo stato di avanzamento delle elaborazioni;

coordinare l’esecuzione della pipeline Nextflow;

comunicare con il servizio di inferenza statistica;

restituire risultati intermedi e finali all’interfaccia utente.



L’orchestrator implementa una gestione asincrona dei task, consentendo l’esecuzione parallela di più analisi cliniche indipendenti.



Inoltre, fornisce endpoint REST per:



upload immagini NIfTI

monitoraggio dello stato dei task

recupero risultati diagnostici

consultazione dello storico elaborazioni 

Nextflow Worker



Il servizio nextflow\_worker esegue la pipeline di preprocessing neuroimaging.



Questo componente utilizza Nextflow per orchestrare workflow riproducibili che includono:



conversione e validazione delle immagini MRI;

segmentazione anatomica cerebrale tramite FreeSurfer;

generazione delle regioni di interesse (ROI);

estrazione delle feature radiomiche tramite PyRadiomics;

aggregazione delle feature in formato tabellare.



L’uso di Nextflow garantisce:



tracciabilità delle elaborazioni;

caching intelligente dei risultati;

riutilizzo dei workflow;

esecuzione modulare delle pipeline.



Il servizio comunica con l’orchestrator tramite API REST e restituisce lo stato di avanzamento delle operazioni di preprocessing 



Model Service



Il servizio model\_service è responsabile dell’esecuzione dell’inferenza diagnostica.



Riceve in ingresso:



vettori di feature radiomiche estratte dalla pipeline Nextflow



e produce:



predizione diagnostica (bvFTD vs HC)

coordinate di embedding nello spazio latente (UMAP)

informazioni sul modello utilizzato



Il servizio recupera automaticamente il modello “champion” registrato tramite MLflow e lo utilizza per effettuare la classificazione supervisionata.



Questa separazione tra preprocessing e inferenza consente di aggiornare i modelli predittivi senza modificare la pipeline neuroimaging.



Frontend



Il frontend è sviluppato utilizzando React e rappresenta l’interfaccia principale di interazione con l’utente clinico.



Consente di:



autenticarsi al sistema;

caricare immagini MRI in formato NIfTI;

monitorare lo stato delle elaborazioni;

visualizzare risultati diagnostici;

esplorare proiezioni UMAP tridimensionali;

consultare lo storico delle analisi effettuate.



L’interfaccia include inoltre strumenti di visualizzazione volumetrica delle immagini neuroanatomiche e pannelli di controllo per l’interpretazione dei risultati.



Il frontend comunica esclusivamente con l’API Gateway e con l’orchestrator tramite richieste HTTP REST 



LLM Assistant



Il servizio LLM assistant fornisce un modulo di supporto interpretativo basato su modelli linguistici avanzati.



Questo componente implementa un sistema di assistenza context-aware che consente di:



interpretare i risultati diagnostici;

fornire spiegazioni clinicamente rilevanti;

contestualizzare le predizioni del modello;

rispondere a domande dell’utente sulla pipeline di analisi;

integrare informazioni provenienti dallo spazio radiomico e dalle proiezioni latenti.



Il servizio utilizza tecniche di Retrieval-Augmented Generation (RAG) per combinare conoscenza clinica strutturata con informazioni specifiche del paziente analizzato.



In questo modo, il sistema supporta il processo decisionale medico mantenendo un approccio human-in-the-loop 

