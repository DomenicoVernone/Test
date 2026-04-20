Assistente LLM clinico

Panoramica generale



Il sistema ClinicalTwin integra un assistente basato su Large Language Models (LLM) progettato per supportare l’interpretazione clinica dei risultati prodotti dalla pipeline radiomica e dal classificatore diagnostico.



L’assistente è implementato come microservizio indipendente:



llm\_service



e fornisce funzionalità di:



interpretazione dei risultati diagnostici

supporto decisionale clinico contestuale

spiegazione dello spazio latente UMAP

interazione conversazionale multi-turno

integrazione con feature radiomiche tramite Spatial RAG 🧠



Questo componente rappresenta un livello semantico superiore rispetto alla pipeline di inferenza statistica.



Architettura del servizio LLM



Il servizio è sviluppato con:



FastAPI



ed espone endpoint REST accessibili dal frontend React.



Struttura principale:



llm\_service/

├── main.py

├── core/

├── routers/

└── services/



Componenti principali:



Modulo	Funzione

main.py	avvio applicazione FastAPI

core/config.py	configurazione ambiente

core/security.py	gestione autenticazione JWT

routers/chat.py	endpoint conversazionale

services/llm\_service.py	logica inferenziale LLM

Modello linguistico utilizzato



Il servizio utilizza modelli LLM accessibili tramite:



Groq API



configurati attraverso la variabile:



GROQ\_API\_KEY



Questa architettura consente:



latenza ridotta

inferenza scalabile

integrazione cloud-ready

aggiornamento dinamico del modello



senza modificare il backend applicativo.



Spatial RAG



L’assistente implementa una strategia:



Spatial Retrieval-Augmented Generation (Spatial RAG)



che estende il paradigma RAG tradizionale integrando informazioni strutturali provenienti dallo spazio latente radiomico.



Le informazioni utilizzate includono:



coordinate UMAP del paziente

cluster diagnostici vicini

distanza dai centroidi HC / bvFTD

feature radiomiche selezionate



Questo approccio consente risposte contestualizzate rispetto alla posizione geometrica del paziente nello spazio delle feature 📊



Memoria conversazionale multi-turno



Il sistema supporta interazioni multi-turno con mantenimento del contesto clinico.



La memoria conversazionale consente di:



riferirsi a risultati precedenti

mantenere continuità interpretativa

approfondire singole ROI

spiegare variazioni radiomiche



Esempio:



Utente: Qual è il risultato diagnostico?

Assistente: Il profilo radiomico è compatibile con bvFTD.



Utente: Quali regioni contribuiscono maggiormente?

Assistente: Le regioni frontali mediali mostrano maggiore deviazione rispetto ai controlli sani.

Endpoint principali



Swagger UI disponibile su:



http://localhost:8002/docs



Endpoint principale:



POST /chat



Request:



{

&#x20; "message": "Interpret the diagnostic result"

}



Response:



{

&#x20; "response": "The radiomic profile suggests compatibility with bvFTD."

}



Le risposte sono generate utilizzando:



contesto radiomico

embedding UMAP

stato pipeline

storico conversazionale

Integrazione con pipeline diagnostica



Il servizio LLM riceve input da:



model\_service



contenenti:



classe predetta

probabilità diagnostica

coordinate UMAP



Esempio:



{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82,

&#x20; "umap\_coordinates": \[1.24, -0.31, 2.08]

}



Queste informazioni vengono trasformate in spiegazioni clinicamente interpretabili.



Integrazione con dashboard clinica



Il frontend React utilizza il componente:



ChatLLM.jsx



per interagire con l’assistente.



L’assistente supporta:



interpretazione predizione diagnostica

spiegazione posizione nello spazio UMAP

descrizione pattern radiomici

supporto alla refertazione esplorativa



Questo consente un’interazione diretta tra medico e sistema AI 🤝



Sicurezza e autenticazione



L’accesso agli endpoint LLM è protetto tramite:



JWT authentication



Configurazione condivisa con:



api\_gateway

orchestrator



Variabili richieste:



SECRET\_KEY



Questo garantisce coerenza del sistema di autenticazione tra microservizi.



Ruolo clinico dell’assistente



L’assistente non sostituisce la decisione clinica, ma fornisce:



interpretazioni contestuali

spiegazioni trasparenti

supporto alla lettura dei risultati

integrazione multimodale tra radiomica e visualizzazione latente



Costituisce quindi un livello di Clinical Decision Support System (CDSS) integrato nella pipeline ClinicalTwin.

