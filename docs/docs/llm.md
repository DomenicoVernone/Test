<style>

:root {
  --primary: #9c27b0;
  --secondary: #6a1b9a;
  --background-soft: #f5ecfa;
  --code-bg: #f4f4f4;
  --text-main: #1f2937;
  --text-soft: #4b5563;
}

body {
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  line-height: 1.65;
  color: var(--text-main);
  max-width: 1100px;
  margin: auto;
  padding: 30px;
}

h1 {
  font-size: 2.2rem;
  margin-bottom: 18px;
}

h2 {
  margin-top: 36px;
  margin-bottom: 12px;
  color: var(--secondary);
}

.llm-box {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 22px;
  border-radius: 8px;
  margin: 26px 0;
}

.code {
  background: var(--code-bg);
  padding: 12px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  white-space: pre;
  overflow-x: auto;
  margin-top: 10px;
}

.inline-code {
  background: var(--code-bg);
  padding: 3px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.highlight {
  font-weight: 600;
  color: var(--secondary);
}

.note {
  margin-top: 12px;
  color: var(--text-soft);
}

.section {
  margin-top: 28px;
}

ul {
  margin-top: 8px;
}

li {
  margin-bottom: 5px;
}

</style>

<h1>Assistente LLM Clinico</h1>

<div class="llm-box">

Il sistema <strong>ClinicalTwin</strong> integra un assistente basato su <strong>Large Language Models (LLM)</strong> progettato per supportare l’interpretazione clinica dei risultati prodotti dalla pipeline radiomica e dal classificatore diagnostico.

L’assistente implementa una strategia <strong>Spatial Retrieval-Augmented Generation (Spatial RAG)</strong> per fornire spiegazioni contestualizzate rispetto alla posizione del paziente nello spazio latente radiomico UMAP.

</div>

<h2>Panoramica generale</h2>

L’assistente è implementato come microservizio indipendente:

<span class="inline-code">llm_service</span>

e fornisce funzionalità di:

<ul>
<li>interpretazione dei risultati diagnostici</li>
<li>supporto decisionale clinico contestuale</li>
<li>spiegazione della posizione nello spazio latente UMAP</li>
<li>interazione conversazionale multi-turno</li>
<li>integrazione con feature radiomiche tramite Spatial RAG</li>
</ul>

<p class="note">
Questo componente rappresenta un livello semantico superiore rispetto alla pipeline di inferenza statistica implementata nel servizio inference_engine.
</p>

<h2>Architettura del servizio LLM</h2>

Il servizio è sviluppato con:

<ul>
<li>FastAPI</li>
</ul>

ed espone endpoint REST accessibili dal frontend React.

Struttura principale:

<div class="code">

llm_service/

├── main.py
├── core/
├── routers/
└── services/

</div>

Componenti principali:

<ul>
<li><strong>main.py</strong> — inizializzazione applicazione FastAPI</li>
<li><strong>core/config.py</strong> — configurazione ambiente runtime</li>
<li><strong>core/security.py</strong> — gestione autenticazione JWT</li>
<li><strong>routers/chat.py</strong> — endpoint conversazionale</li>
<li><strong>services/llm_service.py</strong> — logica inferenziale Spatial RAG</li>
</ul>

<h2>Modello linguistico utilizzato</h2>

Il servizio utilizza modelli LLM accessibili tramite:

<ul>
<li>Groq API</li>
</ul>

configurati attraverso la variabile:

<span class="inline-code">GROQ_API_KEY</span>

Questa architettura consente:

<ul>
<li>bassa latenza inferenziale</li>
<li>scalabilità cloud-native</li>
<li>aggiornamento dinamico del modello linguistico</li>
<li>indipendenza dall’infrastruttura locale</li>
</ul>

<h2>Spatial Retrieval-Augmented Generation (Spatial RAG)</h2>

L’assistente implementa una strategia:

<p class="highlight">Spatial Retrieval-Augmented Generation</p>

che estende il paradigma RAG tradizionale integrando informazioni strutturali provenienti dallo spazio latente radiomico.

Le informazioni utilizzate includono:

<ul>
<li>coordinate UMAP del paziente</li>
<li>cluster diagnostici locali</li>
<li>distanza dai centroidi HC e bvFTD</li>
<li>pattern radiomici regionali selezionati</li>
</ul>

<p class="note">
Questo approccio consente la generazione di spiegazioni contestualizzate rispetto alla posizione geometrica del paziente nello spazio delle feature radiomiche.
</p>

<h2>Memoria conversazionale multi-turno</h2>

Il sistema supporta interazioni multi-turno con mantenimento del contesto clinico.

La memoria conversazionale consente di:

<ul>
<li>riferirsi a risultati precedenti della pipeline</li>
<li>mantenere continuità interpretativa tra richieste successive</li>
<li>approfondire contributi regionali delle ROI</li>
<li>spiegare variazioni radiomiche osservate</li>
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

<span class="inline-code">http://localhost:8002/docs</span>

Endpoint principale:

<div class="code">

POST /chat

</div>

Request:

<div class="code">

{
"message": "Interpret the diagnostic result"
}

</div>

Response:

<div class="code">

{
"response": "The radiomic profile suggests compatibility with bvFTD."
}

</div>

Le risposte sono generate utilizzando:

<ul>
<li>contesto radiomico</li>
<li>embedding UMAP</li>
<li>stato pipeline diagnostica</li>
<li>storico conversazionale</li>
</ul>

<h2>Integrazione con pipeline diagnostica</h2>

Il servizio LLM riceve input dal servizio:

<span class="inline-code">model_service</span>

che fornisce:

<ul>
<li>classe predetta</li>
<li>probabilità diagnostica</li>
<li>coordinate nello spazio latente UMAP</li>
</ul>

Queste informazioni vengono trasformate in spiegazioni clinicamente interpretabili.

<h2>Integrazione con dashboard clinica</h2>

Il frontend React utilizza il componente:

<span class="inline-code">ChatLLM.jsx</span>

per interagire con l’assistente.

L’assistente supporta:

<ul>
<li>interpretazione della predizione diagnostica</li>
<li>spiegazione della posizione nello spazio UMAP</li>
<li>descrizione dei pattern radiomici regionali</li>
<li>supporto alla refertazione esplorativa assistita</li>
</ul>

<h2>Sicurezza e autenticazione</h2>

L’accesso agli endpoint LLM è protetto tramite:

<ul>
<li>JWT authentication</li>
</ul>

Configurazione condivisa con:

<ul>
<li>api_gateway</li>
<li>orchestrator</li>
</ul>

Variabile richiesta:

<span class="inline-code">SECRET_KEY</span>

<p class="note">
Questo garantisce coerenza del sistema di autenticazione tra tutti i microservizi ClinicalTwin.
</p>

<h2>Ruolo clinico dell’assistente</h2>

L’assistente non sostituisce la decisione clinica, ma fornisce:

<ul>
<li>interpretazioni contestuali delle predizioni</li>
<li>spiegazioni trasparenti dei pattern radiomici</li>
<li>supporto alla lettura dello spazio latente diagnostico</li>
<li>integrazione multimodale tra radiomica e visualizzazione UMAP</li>
</ul>

Costituisce quindi un livello avanzato di <strong>Clinical Decision Support System (CDSS)</strong> integrato nella pipeline ClinicalTwin.
