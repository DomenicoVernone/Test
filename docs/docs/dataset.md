<style>

:root {
  --primary: #4caf50;
  --secondary: #2e7d32;
  --background-soft: #edf7ed;
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

h3 {
  margin-top: 22px;
  color: var(--secondary);
}

.dataset-box {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 22px;
  border-radius: 8px;
  margin: 26px 0;
}

.code-block {
  background: var(--code-bg);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  padding: 6px 10px;
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

.section {
  margin-top: 24px;
}

</style>

<h1>Dataset MRI</h1>

<div class="dataset-box">

ClinicalTwin utilizza immagini MRI strutturali in formato <strong>NIfTI</strong> come input della pipeline radiomica per l’estrazione automatizzata di biomarcatori quantitativi regionali utilizzati nella classificazione diagnostica tra <strong>Healthy Controls (HC)</strong> e <strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong>.

</div>

<h2>Formato dei dati MRI: NIfTI</h2>

<p>
La piattaforma ClinicalTwin utilizza immagini di risonanza magnetica cerebrale strutturale nel formato
<span class="highlight">NIfTI (Neuroimaging Informatics Technology Initiative)</span>, standard de facto per la rappresentazione di dati neuroimaging tridimensionali.
</p>

<p>Formati supportati:</p>

<ul>
<li><code>.nii</code></li>
<li><code>.nii.gz</code></li>
</ul>

<p>
Il formato NIfTI consente la rappresentazione compatta di volumi MRI contenenti:
</p>

<ul>
<li>intensità voxel-wise</li>
<li>informazioni spaziali (voxel spacing)</li>
<li>orientamento anatomico</li>
<li>metadati associati all’acquisizione</li>
</ul>

<p class="note">
Per l’utilizzo nella pipeline ClinicalTwin, le immagini devono essere acquisite tramite sequenze T1-weighted ad alta risoluzione, standard nello studio delle alterazioni morfostrutturali neurodegenerative.
</p>

<h2>Preprocessing automatico</h2>

<p>
Le immagini MRI fornite in input vengono sottoposte automaticamente a una pipeline di preprocessing neuroanatomico basata su
<span class="highlight">FreeSurfer</span>.
</p>

<p>
Questa fase consente di ottenere una rappresentazione strutturata, standardizzata e riproducibile dell’anatomia cerebrale del soggetto.
</p>

<p>Non è richiesto preprocessing manuale preliminare da parte dell’utente, purché:</p>

<ul>
<li>l’immagine sia completa</li>
<li>non presenti artefatti severi</li>
<li>sia acquisita con sequenza T1 strutturale standard</li>
</ul>

<p class="note">
Questo approccio garantisce uniformità nella generazione delle feature radiomiche tra soggetti appartenenti a dataset differenti.
</p>

<h2>Estrazione delle regioni di interesse (ROI)</h2>

<p>
Dopo la segmentazione anatomica, la pipeline identifica automaticamente un insieme di
<span class="highlight">78 regioni cerebrali</span>
derivate dagli atlanti FreeSurfer.
</p>

<p>Le ROI comprendono:</p>

<ul>
<li>regioni frontali</li>
<li>regioni temporali</li>
<li>strutture limbiche</li>
<li>strutture sottocorticali profonde</li>
</ul>

<p>
Queste regioni risultano particolarmente informative nello studio della
<strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong>, caratterizzata da alterazioni morfologiche selettive nei lobi frontali e temporali.
</p>

<p class="note">
L’estrazione delle ROI consente di isolare sottovolumi anatomici specifici su cui vengono successivamente calcolate le feature radiomiche regionali.
</p>

<h2>Estrazione delle feature radiomiche</h2>

<p>
A partire dalle ROI segmentate, la pipeline esegue l’estrazione automatizzata di feature radiomiche quantitative tramite
<span class="highlight">PyRadiomics</span>.
</p>

Categorie principali di feature estratte:

<ul>
<li>first-order statistics</li>
<li>texture descriptors</li>
<li>shape features</li>
</ul>

<h3>Feature di primo ordine</h3>

<p>
Descrivono la distribuzione statistica delle intensità voxel all’interno di ciascuna ROI:
</p>

<ul>
<li>media</li>
<li>varianza</li>
<li>skewness</li>
<li>kurtosis</li>
<li>entropia</li>
</ul>

<h3>Feature di texture</h3>

<p>
Caratterizzano la struttura spaziale delle intensità voxel e consentono di catturare pattern microstrutturali non osservabili visivamente:
</p>

<ul>
<li>Gray Level Co-occurrence Matrix (GLCM)</li>
<li>Gray Level Run Length Matrix (GLRLM)</li>
<li>Gray Level Size Zone Matrix (GLSZM)</li>
<li>Neighboring Gray Tone Difference Matrix (NGTDM)</li>
</ul>

<h3>Feature morfologiche</h3>

<p>
Descrivono proprietà geometriche delle regioni segmentate:
</p>

<ul>
<li>volume regionale</li>
<li>superficie</li>
<li>compattezza</li>
<li>sfericità</li>
<li>rapporti dimensionali principali</li>
</ul>

<p class="note">
Queste caratteristiche risultano particolarmente rilevanti nello studio dell’atrofia regionale associata alla degenerazione frontotemporale.
</p>

<h2>Dataset radiomico finale</h2>

<p>
Le feature estratte vengono aggregate in un dataset strutturato in formato CSV:
</p>

<ul>
<li>ogni riga rappresenta un soggetto</li>
<li>ogni colonna rappresenta una feature radiomica</li>
<li>ogni ROI contribuisce con un insieme specifico di descrittori quantitativi</li>
</ul>

Output finale:

<span class="code-block">radiomics_features.csv</span>

<p>
Questo dataset costituisce l’input del modello di classificazione supervisionata utilizzato per distinguere tra:
</p>

<ul>
<li><strong>Healthy Control (HC)</strong></li>
<li><strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong></li>
</ul>

<p class="note">
La trasformazione delle immagini MRI in rappresentazioni numeriche ad alta dimensionalità consente l’applicazione di metodi avanzati di machine learning per il supporto decisionale clinico assistito.
</p>
