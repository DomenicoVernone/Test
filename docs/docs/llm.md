<style>

.llm-box {

&#x20; border-left: 6px solid #9c27b0;

&#x20; background: #f5ecfa;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}



.code {

&#x20; background: #f4f4f4;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; font-family: monospace;

&#x20; white-space: pre;

&#x20; overflow-x: auto;

}



.section {

&#x20; margin-top: 28px;

}

</style>





<h1>Assistente LLM Clinico</h1>





<div class="llm-box">



Il sistema ClinicalTwin integra un assistente basato su Large Language Models (LLM) progettato per supportare l’interpretazione clinica dei risultati prodotti dalla pipeline radiomica e dal classificatore diagnostico.



L’assistente implementa una strategia Spatial Retrieval-Augmented Generation (Spatial RAG) per fornire spiegazioni contestualizzate rispetto alla posizione del paziente nello spazio latente radiomico.



</div>





<h2>Panoramica generale</h2>



L’assistente è implementato come microservizio indipendente:



<code>llm\_service</code>



e fornisce funzionalità di:



<ul>

<li>interpretazione dei risultati diagnostici</li>

<li>supporto decisionale clinico contestuale</li>

<li>spiegazione dello spazio latente UMAP</li>

<li>interazione conversazionale multi-turno</li>

<li>integrazione con feature radiomiche tramite Spatial RAG</li>

</ul>



Questo componente rappresenta un livello semantico superiore rispetto alla pipeline di inferenza statistica.





<h2>Architettura del servizio LLM</h2>



Il servizio è sviluppato con:



<ul>

<li>FastAPI</li>

</ul>



ed espone endpoint REST accessibili dal frontend React.



Struttura principale:



<div class="code">

llm\_service/

├── main.py

├── core/

├── routers/

└── services/

</div>





Componenti principali:



<ul>

<li><strong>main.py</strong> — avvio applicazione FastAPI</li>

<li><strong>core/config.py</strong> — configurazione ambiente</li>

<li><strong>core/security.py</strong> — gestione autenticazione JWT</li>

<li><strong>routers/chat.py</strong> — endpoint conversazionale</li>

<li><strong>services/llm\_service.py</strong> — logica inferenziale LLM</li>

</ul>





<h2>Modello linguistico utilizzato</h2>



Il servizio utilizza modelli LLM accessibili tramite:



<ul>

<li>Groq API</li>

</ul>



configurati attraverso la variabile:



<code>GROQ\_API\_KEY</code>



Questa architettura consente:



<ul>

<li>latenza ridotta</li>

<li>inferenza scalabile</li>

<li>integrazione cloud-ready</li>

<li>aggiornamento dinamico del modello</li>

</ul>



senza modificare il backend applicativo.





<h2>Spatial RAG</h2>



L’assistente implementa una strategia:



<strong>Spatial Retrieval-Augmented Generation (Spatial RAG)</strong>



che estende il paradigma RAG tradizionale integrando informazioni strutturali provenienti dallo spazio latente radiomico.



Le informazioni utilizzate includono:



<ul>

<li>coordinate UMAP del paziente</li>

<li>cluster diagnostici vicini</li>

<li>distanza dai centroidi HC / bvFTD</li>

<li>feature radiomiche selezionate</li>

</ul>



Questo approccio consente risposte contestualizzate rispetto alla posizione geometrica del paziente nello spazio delle feature.





<h2>Memoria conversazionale multi-turno</h2>



Il sistema supporta interazioni multi-turno con mantenimento del contesto clinico.



La memoria conversazionale consente di:



<ul>

<li>riferirsi a risultati precedenti</li>

<li>mantenere continuità interpretativa</li>

<li>approfondire singole ROI</li>

<li>spiegare variazioni radiomiche</li>

</ul>





Esempio:



<div class="code">

Utente: Qual è il risultato diagnostico?



Assistente: Il profilo radiomico è compatibile con bvFTD.



Utente: Quali regioni contribuiscono maggiormente?



Assistente: Le regioni frontali mediali mostrano maggiore deviazione rispetto ai controlli sani.

</div>





<h2>Endpoint principale</h2>



Swagger UI disponibile su:



<code>http://localhost:8002/docs</code>



Endpoint principale:



<div class="code">

POST /chat

</div>





Request:



<div class="code">

{

&#x20; "message": "Interpret the diagnostic result"

}

</div>





Response:



<div class="code">

{

&#x20; "response": "The radiomic profile suggests compatibility with bvFTD."

}

</div>





Le risposte sono generate utilizzando:



<ul>

<li>contesto radiomico</li>

<li>embedding UMAP</li>

<li>stato pipeline</li>

<li>storico conversazionale</li>

</ul>





<h2>Integrazione con pipeline diagnostica</h2>



Il servizio LLM riceve input da:



<code>model\_service</code>



contenenti:



<div class="code">

{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82,

&#x20; "umap\_coordinates": \[1.24, -0.31, 2.08]

}

</div>



Queste informazioni vengono trasformate in spiegazioni clinicamente interpretabili.





<h2>Integrazione con dashboard clinica</h2>



Il frontend React utilizza il componente:



<code>ChatLLM.jsx</code>



per interagire con l’assistente.



L’assistente supporta:



<ul>

<li>interpretazione predizione diagnostica</li>

<li>spiegazione posizione nello spazio UMAP</li>

<li>descrizione pattern radiomici</li>

<li>supporto alla refertazione esplorativa</li>

</ul>



Questo consente un’interazione diretta tra medico e sistema AI.





<h2>Sicurezza e autenticazione</h2>



L’accesso agli endpoint LLM è protetto tramite:



<ul>

<li>JWT authentication</li>

</ul>



Configurazione condivisa con:



<ul>

<li>api\_gateway</li>

<li>orchestrator</li>

</ul>



Variabile richiesta:



<code>SECRET\_KEY</code>



Questo garantisce coerenza del sistema di autenticazione tra microservizi.





<h2>Ruolo clinico dell’assistente</h2>



L’assistente non sostituisce la decisione clinica, ma fornisce:



<ul>

<li>interpretazioni contestuali</li>

<li>spiegazioni trasparenti</li>

<li>supporto alla lettura dei risultati</li>

<li>integrazione multimodale tra radiomica e visualizzazione latente</li>

</ul>



Costituisce quindi un livello di Clinical Decision Support System (CDSS) integrato nella pipeline ClinicalTwin.

