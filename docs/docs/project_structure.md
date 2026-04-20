<style>

.section {

&#x20; border-left: 6px solid #009688;

&#x20; background: #eefaf8;

&#x20; padding: 12px;

&#x20; margin: 16px 0;

&#x20; border-radius: 6px;

}



.code {

&#x20; background: #eeeeee;

&#x20; font-family: monospace;

&#x20; padding: 10px;

&#x20; border-radius: 4px;

&#x20; white-space: pre;

}



.block {

&#x20; margin-top: 18px;

}

</style>





<h1>Struttura del progetto</h1>





<h2>Panoramica generale</h2>



<div class="section">



Il progetto ClinicalTwin è organizzato secondo un’architettura modulare a microservizi containerizzati, in cui ogni componente applicativo è isolato in una directory dedicata e distribuito tramite Docker.



La struttura del repository riflette la separazione tra:



<ul>

<li>servizi backend</li>

<li>pipeline neuroimaging</li>

<li>motore statistico</li>

<li>assistente AI</li>

<li>frontend clinico</li>

<li>documentazione</li>

<li>configurazione del deployment</li>

</ul>



Questa organizzazione facilita la manutenzione del codice, l’estensione della piattaforma e la riproducibilità della pipeline radiomica.



</div>





<h2>Struttura ad alto livello</h2>



La struttura principale del repository è la seguente:



<pre class="code">

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

</pre>



Ogni directory rappresenta un microservizio indipendente del sistema ClinicalTwin.





<h2>docker-compose.yml</h2>



Il file:



<pre class="code">docker-compose.yml</pre>



definisce l’orchestrazione dell’intero stack applicativo.



Specifica:



<ul>

<li>servizi containerizzati</li>

<li>porte esposte</li>

<li>volumi condivisi</li>

<li>dipendenze tra container</li>

<li>variabili d’ambiente</li>

</ul>



Consente l’avvio completo della piattaforma tramite:



<pre class="code">docker compose up --build</pre>





<h2>Directory docs/</h2>



La directory:



<pre class="code">docs/</pre>



contiene la documentazione tecnica del progetto utilizzata da Read the Docs.



Include:



<ul>

<li>descrizione architettura</li>

<li>pipeline neuroimaging</li>

<li>configurazione dataset</li>

<li>installazione</li>

<li>testing</li>

<li>API REST</li>

</ul>



Supporta sia utenti clinici sia sviluppatori.





<h2>api\_gateway/</h2>



Implementa il servizio di autenticazione basato su FastAPI e token JWT.



Struttura:



<pre class="code">

api\_gateway/

├── main.py

├── core/

├── models/

└── routers/

</pre>



Responsabilità principali:



<ul>

<li>registrazione utenti</li>

<li>autenticazione login</li>

<li>generazione token JWT</li>

<li>protezione accesso API</li>

</ul>



Costituisce il punto di ingresso sicuro alla piattaforma.





<h2>orchestrator/</h2>



Contiene il servizio responsabile del coordinamento della pipeline neuroimaging.



Struttura:



<pre class="code">

orchestrator/

├── main.py

├── core/

├── models/

├── routers/

└── services/

</pre>



Responsabilità principali:



<ul>

<li>gestione task MRI</li>

<li>monitoraggio stato elaborazioni</li>

<li>comunicazione con nextflow\_worker</li>

<li>invocazione model\_service</li>

<li>restituzione risultati al frontend</li>

</ul>



Rappresenta il nodo centrale del workflow applicativo.





<h2>model\_service/</h2>



Gestisce l’integrazione con MLflow Model Registry tramite DagsHub.



Struttura:



<pre class="code">

model\_service/

├── main.py

├── core/

└── services/

</pre>



Responsabilità principali:



<ul>

<li>recupero modello champion</li>

<li>versionamento modelli</li>

<li>gestione inferenza radiomica</li>

<li>interfacciamento con inference\_engine</li>

</ul>



Consente aggiornamenti dinamici del classificatore senza modificare la pipeline.





<h2>inference\_engine/</h2>



Implementa il motore statistico della piattaforma in linguaggio R tramite framework Plumber.



Struttura:



<pre class="code">

inference\_engine/

├── api.R

└── R/

</pre>



Responsabilità principali:



<ul>

<li>classificazione KNN</li>

<li>calcolo embedding UMAP 3D</li>

<li>restituzione coordinate spazio latente</li>

<li>integrazione con model\_service</li>

</ul>



Esegue la fase decisionale della pipeline diagnostica.





<h2>llm\_service/</h2>



Implementa l’assistente clinico context-aware basato su modelli linguistici.



Struttura:



<pre class="code">

llm\_service/

├── main.py

├── core/

├── routers/

└── services/

</pre>



Responsabilità principali:



<ul>

<li>interpretazione risultati diagnostici</li>

<li>supporto decisionale assistito</li>

<li>integrazione Spatial RAG</li>

<li>gestione memoria conversazionale multi-turno</li>

</ul>



Fornisce spiegazioni contestualizzate delle predizioni radiomiche.





<h2>nextflow\_worker/</h2>



Contiene la pipeline automatizzata di preprocessing neuroimaging.



Struttura:



<pre class="code">

nextflow\_worker/

├── main.py

├── nextflow/

├── data/

├── freesurfer.dockerfile

├── fsl.dockerfile

└── pyradiomics.dockerfile

</pre>



Responsabilità principali:



<ul>

<li>segmentazione anatomica (FreeSurfer / FastSurfer)</li>

<li>generazione ROI cerebrali</li>

<li>estrazione feature radiomiche</li>

<li>generazione dataset CSV</li>

</ul>



Utilizza il paradigma Docker-out-of-Docker (DooD).





<h2>frontend/</h2>



Contiene l’interfaccia utente clinica sviluppata con React e Vite.



Struttura:



<pre class="code">

frontend/

├── src/

├── components/

├── pages/

├── services/

└── contexts/

</pre>



Responsabilità principali:



<ul>

<li>upload immagini MRI</li>

<li>monitoraggio pipeline</li>

<li>visualizzazione UMAP 3D</li>

<li>rendering volumetrico MRI tramite NiiVue</li>

<li>interazione con assistente AI</li>

</ul>



Costituisce il punto di accesso principale per l’utente finale.





<h2>Flusso operativo tra moduli</h2>



Workflow completo:



<pre class="code">

Frontend

→ API Gateway

→ Orchestrator

→ Nextflow Worker

→ Model Service

→ Inference Engine

→ Dashboard visualization

→ LLM Assistant

</pre>



Questa struttura garantisce separazione funzionale tra acquisizione dati, preprocessing radiomico, inferenza statistica e supporto interpretativo clinico.

