<style>

:root {
  --primary: #ff9800;
  --secondary: #b26a00;
  --background-soft: #fff7e6;
  --code-bg: #eeeeee;
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

.model-box {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 22px;
  border-radius: 8px;
  margin: 26px 0;
}

.code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  background: var(--code-bg);
  padding: 12px;
  border-radius: 6px;
  white-space: pre;
  margin-top: 10px;
}

.inline-code {
  font-family: monospace;
  background: var(--code-bg);
  padding: 3px 6px;
  border-radius: 4px;
}

.note {
  margin-top: 12px;
  color: var(--text-soft);
}

.highlight {
  font-weight: 600;
  color: var(--secondary);
}

ul {
  margin-top: 8px;
}

li {
  margin-bottom: 5px;
}

</style>

<h1>Modelli di Machine Learning</h1>

<div class="model-box">

Il sistema <strong>ClinicalTwin</strong> utilizza modelli di machine learning supervisionato per la diagnosi differenziale tra:

<ul>
<li><strong>Healthy Controls (HC)</strong></li>
<li><strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong></li>
</ul>

I modelli operano su feature radiomiche estratte automaticamente da immagini MRI strutturali tramite pipeline <strong>FreeSurfer / FastSurfer + PyRadiomics</strong>, garantendo riproducibilità e standardizzazione del processo di inferenza diagnostica.

</div>

<h2>Dataset di input</h2>

I modelli ricevono in ingresso un dataset tabellare strutturato:

<div class="code">
radiomics_features.csv
</div>

contenente:

<ul>
<li>feature radiomiche regionali per ciascuna ROI</li>
<li>statistiche di primo ordine</li>
<li>descrittori morfologici</li>
<li>feature di texture multiscala</li>
</ul>

Le feature sono estratte da:

<p class="highlight">78 regioni anatomiche cerebrali derivate dalla parcellazione FreeSurfer</p>

<p class="note">
Questo dataset rappresenta la base quantitativa della pipeline di classificazione supervisionata implementata nel servizio inference_engine.
</p>

<h2>Pipeline di classificazione</h2>

Il workflow di inferenza segue la sequenza:

<div class="code">
Radiomics CSV → normalization → KNN classifier → diagnostic probability → UMAP embedding
</div>

Il risultato finale comprende:

<ul>
<li>classe predetta (HC vs bvFTD)</li>
<li>confidenza predittiva</li>
<li>coordinate nello spazio latente UMAP tridimensionale</li>
</ul>

<h2>Algoritmo di classificazione</h2>

Il motore statistico implementato nel servizio <strong>inference_engine</strong> utilizza un classificatore:

<p class="highlight">K-Nearest Neighbors (KNN)</p>

Questo approccio è particolarmente adatto in contesti radiomici perché:

<ul>
<li>non assume distribuzioni parametriche delle feature</li>
<li>preserva la struttura geometrica dello spazio radiomico</li>
<li>consente interpretabilità locale delle predizioni</li>
<li>supporta integrazione naturale con embedding UMAP</li>
</ul>

<p class="note">
La distanza tra osservazioni viene calcolata nello spazio delle feature radiomiche normalizzate prima della classificazione.
</p>

<h2>Riduzione dimensionale con UMAP</h2>

Per supportare l’interpretabilità clinica del risultato, il sistema utilizza:

<p class="highlight">UMAP (Uniform Manifold Approximation and Projection)</p>

UMAP consente di:

<ul>
<li>ridurre dimensionalità dello spazio radiomico ad alta dimensionalità</li>
<li>preservare relazioni topologiche locali tra soggetti</li>
<li>rappresentare pazienti in uno spazio latente 3D</li>
<li>visualizzare cluster diagnostici nella dashboard clinica</li>
</ul>

<p>
L’embedding risultante viene visualizzato nella dashboard React tramite grafici interattivi Plotly.
</p>

<p class="note">
Ogni nuovo paziente viene proiettato nello spazio latente rispetto al dataset di riferimento utilizzato durante l’addestramento del modello.
</p>

<h2>Model Registry con MLflow</h2>

La gestione dei modelli è affidata al servizio:

<p class="highlight">model_service</p>

che utilizza:

<p class="highlight">MLflow Model Registry (backend DagsHub)</p>

Questo consente:

<ul>
<li>versionamento automatico dei modelli</li>
<li>tracciamento degli esperimenti</li>
<li>selezione dinamica del modello champion</li>
<li>riproducibilità delle predizioni</li>
<li>aggiornamento dinamico senza modifiche al codice applicativo</li>
</ul>

<h2>Variabili principali di configurazione</h2>

<div class="code">
MLFLOW_TRACKING_URI
MLFLOW_TRACKING_USERNAME
DAGSHUB_TOKEN
REPO_OWNER
REPO_NAME
</div>

<h2>Selezione del modello champion</h2>

Durante l’inferenza, il sistema:

<ul>
<li>interroga MLflow Model Registry</li>
<li>recupera il modello marcato come champion</li>
<li>scarica automaticamente la versione attiva</li>
<li>esegue la classificazione sul dataset radiomico corrente</li>
</ul>

<p class="note">
Questo approccio consente l’aggiornamento continuo delle prestazioni diagnostiche senza interrompere il servizio ClinicalTwin.
</p>

<h2>Output del modello</h2>

Il risultato dell’inferenza viene restituito come struttura JSON:

<div class="code">
{
  "prediction": "bvFTD",
  "confidence": 0.82,
  "umap_coordinates": [1.24, -0.31, 2.08]
}
</div>

Include:

<ul>
<li><strong>prediction</strong> — classe diagnostica stimata</li>
<li><strong>confidence</strong> — probabilità associata alla predizione</li>
<li><strong>umap_coordinates</strong> — posizione del soggetto nello spazio latente tridimensionale</li>
</ul>

<h2>Integrazione con assistente AI</h2>

I risultati del modello vengono trasmessi al servizio:

<p class="highlight">llm_service</p>

che li utilizza per generare spiegazioni clinicamente contestualizzate all’interno della dashboard.

<p class="note">
L’integrazione con il modulo Spatial RAG consente all’assistente AI di interpretare la posizione del paziente nello spazio latente rispetto alla popolazione di riferimento.
</p>
