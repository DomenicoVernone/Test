<style>

:root {
  --primary: #2962ff;
  --secondary: #1a3fb8;
  --background-soft: #eef3ff;
  --flow-bg: #f4f6fa;
  --code-bg: #ececec;
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

.section-title {
  margin-top: 40px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 6px;
  color: var(--secondary);
}

.info-box {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 20px;
  margin: 26px 0;
  border-radius: 8px;
}

.pipeline-flow {
  background: var(--flow-bg);
  padding: 16px;
  text-align: center;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  border-radius: 8px;
  font-size: 15px;
  margin: 22px 0;
}

.code-inline {
  background: var(--code-bg);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
}

.badge {
  display: inline-block;
  background: var(--primary);
  color: white;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 12px;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 16px;
}

th {
  background: #f2f2f2;
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
}

.note {
  margin-top: 10px;
  color: var(--text-soft);
}

ul {
  margin-top: 8px;
}

li {
  margin-bottom: 5px;
}

</style>

<h1>Pipeline Nextflow</h1>

<div class="info-box">

La pipeline <strong>Nextflow</strong> rappresenta il nucleo computazionale del sistema ClinicalTwin per il preprocessing neuroimaging e l’estrazione automatizzata delle feature radiomiche da immagini MRI strutturali in formato <strong>NIfTI</strong>.

Coordina l’esecuzione orchestrata dei moduli di segmentazione anatomica, generazione ROI ed estrazione radiomica garantendo riproducibilità, parallelizzazione controllata e portabilità dell’intero workflow computazionale.

</div>

<h2 class="section-title">Workflow computazionale</h2>

Workflow implementato nel file:

<span class="code-inline">
nextflow_worker/nextflow/preprocessing.nf
</span>

<div class="pipeline-flow">

MRI → FreeSurfer / FastSurfer → ROI Masks → Radiomics Extraction → CSV Dataset

</div>

<h2 class="section-title">Struttura della pipeline</h2>

<table>

<tr>
<th>Processo</th>
<th>Funzione</th>
</tr>

<tr>
<td><strong>freesurfer</strong></td>
<td>segmentazione anatomica cerebrale automatizzata</td>
</tr>

<tr>
<td><strong>nifti_converter</strong></td>
<td>conversione dei volumi segmentati in maschere ROI</td>
</tr>

<tr>
<td><strong>roi_creator</strong></td>
<td>costruzione maschere binarie regionali</td>
</tr>

<tr>
<td><strong>feature_extraction</strong></td>
<td>estrazione feature radiomiche tramite PyRadiomics</td>
</tr>

<tr>
<td><strong>csv_collector</strong></td>
<td>aggregazione dataset strutturato finale</td>
</tr>

</table>

<h2 class="section-title">Segmentazione anatomica</h2>

Segmentatori disponibili:

<ul>
<li>FreeSurfer</li>
<li>FastSurfer (GPU-enabled)</li>
</ul>

Configurazione segmentatore:

<span class="code-inline">
nextflow_worker/nextflow/configs/nextflow.config
</span>

Parametro:

<pre>
params.brain_segmenter = "freesurfer"
</pre>

Output generati:

<ul>
<li>volumetrie corticali regionali</li>
<li>strutture sottocorticali segmentate</li>
<li>parcellazione anatomica standardizzata</li>
</ul>

<h2 class="section-title">Generazione ROI</h2>

File configurazione ROI:

<span class="code-inline">
nextflow_worker/data/external/ROI_labels.tsv
</span>

Contiene:

<ul>
<li>etichette FreeSurfer</li>
<li>identificatori numerici regionali</li>
<li>mapping anatomico standardizzato</li>
</ul>

Numero totale ROI:

<div class="pipeline-flow">

78 regioni cerebrali segmentate automaticamente

</div>

<h2 class="section-title">Conversione volumi segmentati</h2>

Processo:

<span class="badge">nifti_converter</span>

Operazioni principali:

<ul>
<li>selezione automatica ROI target</li>
<li>generazione maschere binarie regionali</li>
<li>normalizzazione formato NIfTI</li>
</ul>

Output prodotto:

<pre>
ROI_mask.nii.gz
</pre>

<h2 class="section-title">Estrazione feature radiomiche</h2>

Estrazione eseguita tramite:

<span class="badge">PyRadiomics</span>

Configurazione:

<span class="code-inline">
nextflow_worker/data/external/pyradiomics.yaml
</span>

Categorie principali di feature estratte:

<ul>
<li>shape descriptors (volume, surface, compactness)</li>
<li>first-order statistics (mean, variance, skewness)</li>
<li>texture features (GLCM, GLRLM, GLSZM)</li>
<li>intensity distribution metrics</li>
</ul>

<h2 class="section-title">Generazione dataset CSV</h2>

Processo:

<span class="badge">csv_collector</span>

Output finale:

<pre>
radiomics_features.csv
</pre>

Contiene:

<ul>
<li>feature radiomiche per ciascuna ROI</li>
<li>dataset compatibile con pipeline ML</li>
<li>input diretto per model_service</li>
</ul>

<h2 class="section-title">Parametri configurabili</h2>

File configurazione:

<span class="code-inline">
nextflow_worker/nextflow/configs/nextflow.config
</span>

<table>

<tr>
<th>Parametro</th>
<th>Descrizione</th>
</tr>

<tr>
<td>maxforks</td>
<td>numero massimo processi paralleli Nextflow</td>
</tr>

<tr>
<td>fastsurfer_threads</td>
<td>thread CPU per FastSurfer</td>
</tr>

<tr>
<td>fastsurfer_device</td>
<td>selezione device: cpu oppure cuda</td>
</tr>

<tr>
<td>fastsurfer_3T</td>
<td>ottimizzazione pipeline per scanner 3T</td>
</tr>

<tr>
<td>pyradiomics_jobs</td>
<td>parallelismo estrazione feature</td>
</tr>

<tr>
<td>brain_segmenter</td>
<td>segmentatore selezionato (freesurfer / fastsurfer)</td>
</tr>

</table>

<h2 class="section-title">Architettura Docker-out-of-Docker (DooD)</h2>

<div class="pipeline-flow">

Nextflow (container) → Docker Host → Pipeline Containers

</div>

Questo significa che:

<ul>
<li>Nextflow viene eseguito nel container <strong>nextflow_worker</strong></li>
<li>i container scientifici vengono eseguiti direttamente sul Docker host</li>
<li>le immagini devono essere pre-costruite localmente prima dell’avvio dello stack</li>
</ul>

Build immagini richieste:

<pre>

docker build -t clinical-freesurfer -f nextflow_worker/freesurfer.dockerfile nextflow_worker/

docker build -t clinical-fsl -f nextflow_worker/fsl.dockerfile nextflow_worker/

docker build -t clinical-pyradiomics -f nextflow_worker/pyradiomics.dockerfile nextflow_worker/

</pre>

<h2 class="section-title">Output della pipeline</h2>

<table>

<tr>
<th>Output</th>
<th>Descrizione</th>
</tr>

<tr>
<td>ROI masks</td>
<td>maschere anatomiche segmentate regionalmente</td>
</tr>

<tr>
<td>radiomics_features.csv</td>
<td>dataset feature radiomiche per inferenza diagnostica</td>
</tr>

<tr>
<td>Nextflow logs</td>
<td>tracciamento completo esecuzione pipeline</td>
</tr>

</table>

<p class="note">
Il dataset CSV generato viene successivamente utilizzato dal <strong>model_service</strong> per la classificazione diagnostica e la proiezione del soggetto nello spazio latente <strong>UMAP</strong>.
</p>
