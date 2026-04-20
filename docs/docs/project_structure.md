<style>

:root {
  --primary: #009688;
  --secondary: #00695c;
  --background-soft: #eefaf8;
  --code-bg: #f5f7f9;
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
  margin-bottom: 20px;
}

h2 {
  margin-top: 35px;
  margin-bottom: 12px;
  color: var(--secondary);
}

.section {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 20px;
  margin: 24px 0;
  border-radius: 8px;
}

.code {
  background: var(--code-bg);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  padding: 14px;
  border-radius: 6px;
  white-space: pre;
  overflow-x: auto;
  margin-top: 10px;
}

.subtitle {
  font-weight: 600;
  margin-top: 10px;
}

.note {
  margin-top: 12px;
  color: var(--text-soft);
}

ul {
  margin-top: 8px;
}

li {
  margin-bottom: 5px;
}

</style>

<h1>Struttura del progetto ClinicalTwin</h1>

<h2>Panoramica generale</h2>

<div class="section">

<p>
Il progetto <strong>ClinicalTwin</strong> è organizzato secondo un’architettura modulare a microservizi containerizzati, in cui ogni componente applicativo è isolato in una directory dedicata e distribuito tramite Docker.
</p>

<p>La struttura del repository riflette la separazione tra:</p>

<ul>
<li>servizi backend applicativi</li>
<li>pipeline neuroimaging automatizzata</li>
<li>motore statistico di inferenza</li>
<li>assistente AI context-aware</li>
<li>frontend clinico interattivo</li>
<li>documentazione tecnica</li>
<li>configurazione del deployment</li>
</ul>

<p class="note">
Questa organizzazione garantisce elevata manutenibilità, scalabilità architetturale e riproducibilità computazionale della pipeline radiomica.
</p>

</div>

<h2>Struttura ad alto livello del repository</h2>

<p>La struttura principale del progetto è la seguente:</p>

<pre class="code">
Tesi-FTD/

├── docker-compose.yml
├── .env.example
├── docs/
├── api_gateway/
├── orchestrator/
├── model_service/
├── inference_engine/
├── llm_service/
├── nextflow_worker/
└── frontend/
</pre>

<p class="note">
Ogni directory rappresenta un microservizio indipendente della piattaforma ClinicalTwin.
</p>

<h2>docker-compose.yml</h2>

<div class="section">

<p>
Il file <strong>docker-compose.yml</strong> definisce l’orchestrazione completa dello stack applicativo.
</p>

<p>Specifica:</p>

<ul>
<li>servizi containerizzati</li>
<li>porte esposte</li>
<li>volumi persistenti condivisi</li>
<li>dipendenze tra microservizi</li>
<li>variabili d’ambiente di configurazione</li>
</ul>

<p>Consente l’avvio dell’intera piattaforma tramite:</p>

<pre class="code">docker compose up --build</pre>

</div>

<h2>Directory docs/</h2>

<div class="section">

<p>
La directory <strong>docs/</strong> contiene la documentazione tecnica utilizzata da Read the Docs.
</p>

<p>Include:</p>

<ul>
<li>descrizione architettura software</li>
<li>pipeline neuroimaging</li>
<li>configurazione dataset MRI</li>
<li>procedure di installazione</li>
<li>strategie di testing</li>
<li>documentazione API REST</li>
</ul>

<p class="note">
Supporta sia utenti clinici sia sviluppatori della piattaforma.
</p>

</div>

<h2>api_gateway/</h2>

<div class="section">

<p>
Implementa il servizio di autenticazione basato su <strong>FastAPI</strong> e token <strong>JWT</strong>.
</p>

<pre class="code">
api_gateway/

├── main.py
├── core/
├── models/
└── routers/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>registrazione utenti</li>
<li>autenticazione login</li>
<li>generazione token JWT</li>
<li>protezione accesso API</li>
</ul>

</div>

<h2>orchestrator/</h2>

<div class="section">

<p>
Servizio responsabile del coordinamento della pipeline neuroimaging automatizzata.
</p>

<pre class="code">
orchestrator/

├── main.py
├── core/
├── models/
├── routers/
└── services/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>gestione task MRI asincroni</li>
<li>monitoraggio stato elaborazioni</li>
<li>comunicazione con nextflow_worker</li>
<li>invocazione model_service</li>
<li>restituzione risultati al frontend</li>
</ul>

</div>

<h2>model_service/</h2>

<div class="section">

<p>
Gestisce l’integrazione con <strong>MLflow Model Registry</strong> tramite <strong>DagsHub</strong>.
</p>

<pre class="code">
model_service/

├── main.py
├── core/
└── services/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>recupero modello champion</li>
<li>versionamento modelli</li>
<li>gestione inferenza radiomica</li>
<li>interfacciamento con inference_engine</li>
</ul>

</div>

<h2>inference_engine/</h2>

<div class="section">

<p>
Implementa il motore statistico della piattaforma in linguaggio <strong>R</strong> tramite framework <strong>Plumber</strong>.
</p>

<pre class="code">
inference_engine/

├── api.R
└── R/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>classificazione KNN</li>
<li>calcolo embedding UMAP 3D</li>
<li>restituzione coordinate spazio latente</li>
<li>integrazione con model_service</li>
</ul>

</div>

<h2>llm_service/</h2>

<div class="section">

<p>
Implementa l’assistente clinico context-aware basato su modelli linguistici con approccio <strong>Spatial RAG</strong>.
</p>

<pre class="code">
llm_service/

├── main.py
├── core/
├── routers/
└── services/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>interpretazione risultati diagnostici</li>
<li>supporto decisionale assistito</li>
<li>integrazione Spatial RAG</li>
<li>gestione memoria conversazionale multi-turno</li>
</ul>

</div>

<h2>nextflow_worker/</h2>

<div class="section">

<p>
Contiene la pipeline automatizzata di preprocessing neuroimaging orchestrata tramite <strong>Nextflow</strong>.
</p>

<pre class="code">
nextflow_worker/

├── main.py
├── nextflow/
├── data/
├── freesurfer.dockerfile
├── fsl.dockerfile
└── pyradiomics.dockerfile
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>segmentazione anatomica (FreeSurfer / FastSurfer)</li>
<li>generazione ROI cerebrali</li>
<li>estrazione feature radiomiche</li>
<li>produzione dataset CSV strutturati</li>
</ul>

<p class="note">
La pipeline utilizza il paradigma Docker-out-of-Docker (DooD) per l’esecuzione dei container scientifici.
</p>

</div>

<h2>frontend/</h2>

<div class="section">

<p>
Contiene l’interfaccia clinica sviluppata con <strong>React</strong> e <strong>Vite</strong>.
</p>

<pre class="code">
frontend/

├── src/
├── components/
├── pages/
├── services/
└── contexts/
</pre>

<p class="subtitle">Responsabilità principali:</p>

<ul>
<li>upload immagini MRI</li>
<li>monitoraggio pipeline</li>
<li>visualizzazione UMAP 3D</li>
<li>rendering volumetrico MRI tramite NiiVue</li>
<li>interazione con assistente AI</li>
</ul>

</div>

<h2>Flusso operativo tra moduli</h2>

<div class="section">

<p>
La struttura modulare del repository garantisce una chiara separazione tra:
</p>

<ul>
<li>acquisizione dati MRI</li>
<li>preprocessing radiomico automatizzato</li>
<li>inferenza statistica supervisionata</li>
<li>visualizzazione spazio latente UMAP</li>
<li>supporto interpretativo tramite assistente AI</li>
</ul>

<p class="note">
Questa architettura consente elevata scalabilità, aggiornamento indipendente dei microservizi e riproducibilità dell’intero workflow clinico-computazionale.
</p>

</div>
