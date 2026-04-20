Testing



Questa sezione descrive le procedure di verifica funzionale dei principali componenti della piattaforma ClinicalTwin, al fine di garantire il corretto funzionamento dello stack applicativo e della pipeline di analisi neuroimaging.



Le attività di testing includono:



verifica dei container Docker

test della pipeline Nextflow

validazione del classificatore diagnostico

test della dashboard clinica

Verifica dei container Docker



Dopo l’avvio dello stack applicativo, verificare che tutti i servizi risultino attivi:



docker compose ps



Devono risultare in stato running i seguenti container:



api\_gateway

orchestrator

nextflow\_worker

model\_service

inference\_engine

llm\_service

frontend



Per controllare eventuali errori nei log:



docker compose logs -f



Oppure per un singolo servizio:



docker compose logs -f orchestrator

Test della pipeline Nextflow



La pipeline neuroimaging può essere verificata caricando una MRI cerebrale in formato NIfTI (.nii o .nii.gz) tramite la dashboard.



Procedura:



accedere alla dashboard clinica

caricare un file MRI

avviare l’elaborazione

monitorare lo stato del task



Durante l’esecuzione devono essere completate le seguenti fasi:



MRI → FreeSurfer → ROI extraction → Radiomics → CSV generation



Lo stato del workflow può essere monitorato nei log del servizio:



docker compose logs -f nextflow\_worker



Il completamento della pipeline produce un dataset radiomico in formato CSV utilizzato dal classificatore.



Test del classificatore diagnostico



Il servizio model\_service recupera automaticamente il modello champion registrato su MLflow tramite DagsHub.



Per verificare il corretto funzionamento del classificatore:



eseguire una pipeline completa

attendere la fase di inferenza

verificare la restituzione della predizione



Output atteso:



classe diagnostica (bvFTD oppure HC)

coordinate nello spazio latente UMAP

probabilità associata alla classificazione



Eventuali errori possono essere verificati tramite:



docker compose logs -f model\_service



oppure:



docker compose logs -f inference\_engine

Test della dashboard clinica



Il frontend React consente la visualizzazione interattiva dei risultati.



Verificare:



Upload MRI



Caricamento corretto file:



. nii

. nii.gz

Visualizzazione multiplanare



Controllare la corretta visualizzazione delle sezioni:



assiale

coronale

sagittale



tramite viewer NiiVue



Proiezione spazio latente UMAP



Dopo l’inferenza, verificare la comparsa:



embedding tridimensionale

posizione del paziente

confronto con dataset di riferimento

Assistente AI clinico



Testare l’assistente LLM verificando:



risposta a query contestuali

interpretazione della predizione

supporto alla navigazione dello spazio latente

Verifica completa del sistema



Il sistema è considerato correttamente funzionante quando:



tutti i container risultano attivi ✅

la pipeline Nextflow termina senza errori

viene generato il dataset radiomico

il classificatore restituisce una predizione

la dashboard visualizza correttamente UMAP e MRI



In queste condizioni la piattaforma ClinicalTwin è pronta per l’utilizzo in ambiente di ricerca clinica sperimentale.

