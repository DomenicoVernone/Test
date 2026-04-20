<style>
.dataset-box {
  border-left: 6px solid #4caf50;
  background: #edf7ed;
  padding: 18px;
  border-radius: 6px;
  margin: 20px 0;
}

.code-block {
  background: #eeeeee;
  font-family: monospace;
  padding: 6px 10px;
  border-radius: 4px;
}

.section {
  margin-top: 22px;
}
</style>


<h1>Dataset MRI</h1>


<div class="dataset-box">

ClinicalTwin utilizza immagini MRI strutturali in formato NIfTI come input della pipeline radiomica.

</div>


<h2>Formato dei dati MRI: NIfTI</h2>

La piattaforma ClinicalTwin utilizza immagini di risonanza magnetica strutturale cerebrale in formato NIfTI (Neuroimaging Informatics Technology Initiative), che rappresenta lo standard de facto per la memorizzazione e la condivisione di dati neuroimaging tridimensionali.

I formati supportati includono:

<ul>
<li><code>.nii</code></li>
<li><code>.nii.gz</code></li>
</ul>

Il formato NIfTI consente la rappresentazione compatta di volumi MRI tridimensionali contenenti:

<ul>
<li>intensità voxel-wise</li>
<li>informazioni spaziali (voxel spacing)</li>
<li>orientamento anatomico</li>
<li>metadati associati all’acquisizione</li>
</ul>

Per l’utilizzo all’interno della pipeline ClinicalTwin, le immagini devono essere acquisite tramite sequenze T1-weighted ad alta risoluzione, generalmente impiegate nello studio delle alterazioni morfostrutturali associate alle patologie neurodegenerative.


<h2>Preprocessing richiesto</h2>

Le immagini MRI fornite in input vengono sottoposte automaticamente a una pipeline di preprocessing neuroanatomico basata su strumenti standardizzati di neuroimaging.

Le principali operazioni includono:

<ul>
<li>normalizzazione dell’orientamento spaziale</li>
<li>rimozione del tessuto extracranico (skull stripping)</li>
<li>segmentazione dei tessuti cerebrali</li>
<li>ricostruzione delle superfici corticali</li>
<li>parcellizzazione anatomica regionale</li>
</ul>

Queste operazioni sono eseguite tramite FreeSurfer, che consente di ottenere una rappresentazione strutturata e riproducibile dell’anatomia cerebrale del soggetto.

Non è richiesto preprocessing manuale preliminare da parte dell’utente, purché:

<ul>
<li>l’immagine sia completa</li>
<li>non presenti artefatti severi</li>
<li>sia acquisita con sequenza T1 strutturale standard</li>
</ul>

Questo approccio garantisce uniformità nella generazione delle feature tra soggetti diversi.


<h2>ROI extraction</h2>

Dopo la segmentazione anatomica, la pipeline identifica automaticamente un insieme di regioni di interesse (Regions of Interest, ROI) corrispondenti a strutture cerebrali corticali e sottocorticali rilevanti per la classificazione diagnostica.

Numero ROI:

<strong>78 regioni cerebrali</strong>

derivate da atlanti FreeSurfer.

Le ROI comprendono:

<ul>
<li>regioni frontali</li>
<li>regioni temporali</li>
<li>strutture limbiche</li>
<li>strutture sottocorticali profonde</li>
</ul>

Queste regioni rappresentano aree particolarmente informative nello studio della behavioral variant Frontotemporal Dementia (bvFTD), caratterizzata da alterazioni morfologiche selettive nei lobi frontali e temporali.

L’estrazione delle ROI consente di isolare sottovolumi anatomici specifici sui quali vengono successivamente calcolate le feature radiomiche.


<h2>Radiomics extraction</h2>

A partire dalle ROI segmentate, la pipeline esegue l’estrazione automatica di feature radiomiche quantitative tramite strumenti dedicati (PyRadiomics).

Feature estratte:

<ul>
<li>first-order statistics</li>
<li>texture descriptors</li>
<li>shape features</li>
</ul>


<h3>Feature di primo ordine</h3>

Descrivono la distribuzione statistica delle intensità voxel all’interno della ROI:

<ul>
<li>media</li>
<li>varianza</li>
<li>skewness</li>
<li>kurtosis</li>
<li>entropia</li>
</ul>


<h3>Feature di texture</h3>

Caratterizzano la struttura spaziale delle intensità voxel:

<ul>
<li>Gray Level Co-occurrence Matrix (GLCM)</li>
<li>Gray Level Run Length Matrix (GLRLM)</li>
<li>Gray Level Size Zone Matrix (GLSZM)</li>
<li>Neighboring Gray Tone Difference Matrix (NGTDM)</li>
</ul>

Queste metriche consentono di catturare pattern microstrutturali non osservabili visivamente.


<h3>Feature morfologiche</h3>

Descrivono proprietà geometriche delle regioni segmentate:

<ul>
<li>volume regionale</li>
<li>superficie</li>
<li>compattezza</li>
<li>sfericità</li>
<li>rapporti dimensionali principali</li>
</ul>

Queste caratteristiche risultano particolarmente rilevanti nello studio dell’atrofia regionale associata alla degenerazione frontotemporale.


<h2>Dataset radiomico finale</h2>

Le feature estratte vengono aggregate in un dataset strutturato in formato CSV, in cui:

<ul>
<li>ogni riga rappresenta un soggetto</li>
<li>ogni colonna rappresenta una feature radiomica</li>
<li>ogni ROI contribuisce con un insieme specifico di descrittori quantitativi</li>
</ul>

Output finale:

<code class="code-block">radiomics_features.csv</code>

Questo dataset costituisce l’input del modello di classificazione supervisionata utilizzato per la distinzione tra:

<ul>
<li>Healthy Control (HC)</li>
<li>behavioral variant Frontotemporal Dementia (bvFTD)</li>
</ul>

La trasformazione delle immagini MRI in rappresentazioni numeriche ad alta dimensionalità consente l’applicazione di metodi avanzati di machine learning per il supporto decisionale clinico assistito.