Configurazione avanzata



Questa sezione descrive le principali variabili di configurazione utilizzate dalla piattaforma ClinicalTwin.

Le impostazioni sono definite nei file .env dei singoli microservizi e consentono di personalizzare autenticazione, pipeline radiomica, gestione modelli e servizi AI.



Variabili di autenticazione



Le variabili seguenti devono essere identiche nei servizi che utilizzano JWT.



SECRET\_KEY



Servizi:



api\_gateway

orchestrator

llm\_service



Descrizione:



Chiave utilizzata per la firma dei token JWT. Deve essere condivisa tra i servizi per garantire autenticazione coerente tra microservizi.



Esempio:



SECRET\_KEY=my\_super\_secret\_key

Configurazione assistente AI

GROQ\_API\_KEY



Servizio:



llm\_service



Descrizione:



Chiave API utilizzata per accedere ai modelli linguistici tramite piattaforma Groq.



Esempio:



GROQ\_API\_KEY=your\_api\_key\_here



Senza questa variabile l’assistente clinico non sarà disponibile nella dashboard.



Configurazione Model Registry



Le seguenti variabili consentono l’integrazione con MLflow e DagsHub per il versionamento dei modelli diagnostici.



MLFLOW\_TRACKING\_URI



Servizio:



model\_service



Descrizione:



URL del server MLflow remoto.



Esempio:



MLFLOW\_TRACKING\_URI=https://dagshub.com/<user>/<repo>.mlflow

MLFLOW\_TRACKING\_USERNAME



Descrizione:



Username DagsHub utilizzato per autenticazione al Model Registry.



DAGSHUB\_TOKEN



Descrizione:



Token personale DagsHub utilizzato come password per accesso al Model Registry.



REPO\_OWNER



Descrizione:



Username proprietario del repository MLflow su DagsHub.



REPO\_NAME



Descrizione:



Nome del repository contenente i modelli registrati.



Configurazione GPU (opzionale)

MIG\_DEVICE



Descrizione:



UUID della MIG instance GPU utilizzata da FastSurfer.



Esempio:



MIG\_DEVICE=MIG-xxxxxxxxxxxxxxxx



Se non impostata:



viene utilizzata GPU standard

oppure CPU tramite FreeSurfer

Configurazione volumi condivisi

HOST\_SHARED\_VOLUME\_DIR



Descrizione:



Percorso host utilizzato per la condivisione dati tra container.



Uso consigliato:



Linux bare metal → impostare manualmente

Docker Desktop (Windows/macOS) → lasciare vuoto



Esempio:



HOST\_SHARED\_VOLUME\_DIR=/mnt/shared\_volume

Configurazione pipeline Nextflow



I parametri della pipeline neuroimaging sono definiti nel file:



nextflow\_worker/nextflow/configs/nextflow.config



Principali parametri disponibili:



params.brain\_segmenter



Segmentatore utilizzato:



freesurfer

fastsurfer



Default:



freesurfer

params.maxforks



Numero massimo di pipeline eseguibili in parallelo.



Esempio:



params.maxforks = 1

params.fastsurfer\_threads



Numero thread CPU utilizzati da FastSurfer.



Esempio:



params.fastsurfer\_threads = 8

params.pyradiomics\_jobs



Numero processi paralleli per estrazione radiomica.



Esempio:



params.pyradiomics\_jobs = 4

Configurazione file radiomici esterni



La pipeline richiede due file statici:



nextflow\_worker/data/external/



Contenuto:



File	Descrizione

ROI\_labels.tsv	Etichette delle 78 ROI cerebrali

pyradiomics.yaml	Parametri estrazione feature



Questi file sono necessari per l’esecuzione della pipeline radiomica.



Configurazione privacy e sicurezza



ClinicalTwin supporta ambienti di ricerca clinica sperimentale tramite:



autenticazione JWT

isolamento container Docker

gestione separata Model Registry

accesso controllato ai servizi LLM



L’utilizzo in ambiente clinico reale richiede integrazione con sistemi conformi alle normative GDPR e infrastrutture sanitarie certificate.

