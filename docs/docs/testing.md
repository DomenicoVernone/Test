Testing

Panoramica della strategia di test



La piattaforma ClinicalTwin integra una strategia di testing multilivello finalizzata a garantire il corretto funzionamento dei servizi containerizzati, della pipeline neuroimaging, del modulo di classificazione diagnostica e dell’interfaccia utente clinica.



Le attività di verifica comprendono:



validazione dell’avvio dei container Docker;

verifica dell’esecuzione della pipeline Nextflow;

test del servizio di inferenza diagnostica;

test funzionali della dashboard web.



Questo approccio consente di assicurare affidabilità, riproducibilità e integrità dell’intero workflow computazionale 🧪



Test dei container Docker



Il primo livello di verifica riguarda il corretto avvio dei servizi containerizzati che costituiscono l’infrastruttura della piattaforma.



L’avvio del sistema viene eseguito tramite:



docker compose up --build



Una volta completata l’inizializzazione, è possibile verificare lo stato dei container mediante:



docker compose ps



Tutti i servizi devono risultare nello stato:



Up



In particolare, devono essere attivi:



api\_gateway

orchestrator

nextflow\_worker

model\_service

llm\_service

frontend



Eventuali anomalie possono essere analizzate consultando i log:



docker compose logs -f



Questa fase garantisce la corretta inizializzazione dell’infrastruttura distribuita ⚙️



Test della pipeline Nextflow



Il secondo livello di testing riguarda la validazione della pipeline di preprocessing neuroimaging gestita dal servizio nextflow\_worker.



Il test consiste nel caricamento di un’immagine MRI in formato NIfTI tramite la dashboard oppure tramite endpoint API.



Durante l’esecuzione devono essere completati correttamente i seguenti step:



avvio del workflow Nextflow

segmentazione anatomica tramite FreeSurfer

generazione delle ROI cerebrali

estrazione delle feature radiomiche

produzione del dataset CSV finale



Lo stato della pipeline può essere monitorato tramite:



GET /status/{task\_id}



oppure attraverso i log del container:



docker compose logs nextflow\_worker



Il completamento senza errori della pipeline conferma la corretta configurazione degli strumenti di neuroimaging 🔬



Test del classificatore diagnostico



Il terzo livello di testing riguarda la verifica del servizio model\_service, responsabile dell’inferenza diagnostica.



Una volta completata l’estrazione delle feature radiomiche, il sistema invia automaticamente il dataset al classificatore supervisionato.



Il servizio restituisce:



classe predetta (bvFTD oppure HC)

coordinate nello spazio latente UMAP

informazioni sul modello utilizzato



Il corretto funzionamento del classificatore può essere verificato controllando:



risposta dell’endpoint di inferenza

presenza della predizione nel task registrato

aggiornamento dello stato del workflow



Questa fase garantisce l’integrazione corretta tra preprocessing radiomico e modello predittivo 📊



Test della dashboard clinica



L’ultimo livello di testing riguarda la verifica funzionale dell’interfaccia utente sviluppata in React.



L’accesso alla dashboard avviene tramite:



http://localhost:3000



Le principali operazioni da verificare includono:



registrazione di un nuovo utente

autenticazione tramite login

caricamento di immagini MRI in formato NIfTI

visualizzazione dello stato delle analisi

consultazione dello storico dei task

visualizzazione della proiezione UMAP tridimensionale

interazione con l’assistente LLM



Il corretto funzionamento della dashboard conferma l’integrazione tra frontend e servizi backend del sistema 🌐



Validazione end-to-end della pipeline



Il test completo del sistema consiste nell’esecuzione di un workflow end-to-end:



Upload MRI → preprocessing → estrazione feature → classificazione → visualizzazione risultati



Il completamento dell’intero processo senza errori rappresenta la verifica finale della corretta configurazione della piattaforma ClinicalTwin e della sua operatività in ambiente locale 🧠

