Modelli di Machine Learning

Panoramica generale



Il sistema ClinicalTwin utilizza modelli di machine learning supervisionato per la diagnosi differenziale tra:



soggetti sani (HC, Healthy Controls)

pazienti affetti da bvFTD (behavioral variant Frontotemporal Dementia)



I modelli operano su feature radiomiche estratte automaticamente da immagini MRI strutturali tramite pipeline FreeSurfer/FastSurfer + PyRadiomics.



L’infrastruttura di inferenza è progettata per supportare:



versionamento dei modelli

selezione dinamica del modello attivo (champion model)

riproducibilità sperimentale

integrazione con dashboard clinica e assistente AI

Dataset di input



I modelli ricevono in ingresso un dataset tabellare:



radiomics\_features.csv



contenente:



feature radiomiche per ciascuna ROI

statistiche di primo ordine

descrittori morfologici

feature di texture multiscala



Le feature sono estratte da:



78 regioni anatomiche cerebrali (ROI)



derivate dalla parcellazione FreeSurfer.



Pipeline di classificazione



Il workflow di inferenza segue la sequenza:



Radiomics CSV → preprocessing → classificatore → probabilità diagnostica → embedding UMAP



Il risultato finale comprende:



classe predetta (HC vs bvFTD)

confidenza predittiva

coordinate nello spazio latente UMAP 3D

Algoritmo di classificazione



Il motore statistico implementato nel servizio inference\_engine utilizza un classificatore:



K-Nearest Neighbors (KNN)



Questo approccio è particolarmente adatto in contesti radiomici perché:



non assume distribuzioni parametriche

preserva la struttura geometrica dello spazio delle feature

consente interpretabilità locale

facilita la visualizzazione nello spazio latente



La distanza tra osservazioni viene calcolata nello spazio delle feature radiomiche normalizzate.



Riduzione dimensionale con UMAP



Per supportare l’interpretabilità clinica del risultato, il sistema utilizza:



UMAP (Uniform Manifold Approximation and Projection)



UMAP consente di:



ridurre dimensionalità dello spazio radiomico

preservare relazioni topologiche locali

rappresentare pazienti in uno spazio latente 3D

visualizzare cluster diagnostici



L’embedding risultante viene mostrato nella dashboard React tramite grafici interattivi Plotly 📊



Ogni nuovo paziente viene proiettato nello spazio latente rispetto al dataset di riferimento.



Model registry con MLflow



La gestione dei modelli è affidata al servizio:



model\_service



che utilizza:



MLflow Model Registry (DagsHub backend)



Questo consente:



versionamento automatico dei modelli

tracciamento esperimenti

selezione del modello champion

riproducibilità delle predizioni

aggiornamento dinamico senza modifiche al codice



Variabili principali di configurazione:



MLFLOW\_TRACKING\_URI

MLFLOW\_TRACKING\_USERNAME

DAGSHUB\_TOKEN

REPO\_OWNER

REPO\_NAME

Selezione del modello champion



Durante l’inferenza, il sistema:



interroga MLflow

recupera il modello marcato come champion

scarica automaticamente la versione attiva

esegue la classificazione sul dataset radiomico



Questo approccio permette l’aggiornamento continuo delle prestazioni diagnostiche senza interrompere il servizio.



Output del modello



Il risultato dell’inferenza è restituito come struttura JSON:



{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82,

&#x20; "umap\_coordinates": \[1.24, -0.31, 2.08]

}



Include:



Campo	Descrizione

prediction	classe diagnostica stimata

confidence	probabilità associata

umap\_coordinates	posizione nello spazio latente



Queste informazioni vengono visualizzate nella dashboard clinica e utilizzate dall’assistente LLM per generare spiegazioni contestuali 🧠



Integrazione con assistente AI



I risultati del modello vengono trasmessi al servizio:



llm\_service



che utilizza un approccio:



Spatial RAG (Retrieval-Augmented Generation)



per integrare:



coordinate UMAP

cluster diagnostici

profilo radiomico del paziente



nelle risposte generate per il medico.



Questo consente interpretazioni clinicamente assistite e contestualizzate rispetto allo spazio latente del dataset.

