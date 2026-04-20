<style>

.section-box {

&#x20; border-left: 5px solid #3f51b5;

&#x20; background: #f5f7ff;

&#x20; padding: 12px 16px;

&#x20; margin: 18px 0;

&#x20; border-radius: 6px;

}



.pipeline-box {

&#x20; background: #f1f3f4;

&#x20; border-radius: 8px;

&#x20; padding: 14px;

&#x20; font-family: monospace;

&#x20; text-align: center;

&#x20; font-size: 16px;

&#x20; margin: 20px 0;

}



.code-path {

&#x20; background: #eeeeee;

&#x20; padding: 4px 8px;

&#x20; border-radius: 4px;

&#x20; font-family: monospace;

}



.badge {

&#x20; display: inline-block;

&#x20; padding: 4px 10px;

&#x20; background: #3f51b5;

&#x20; color: white;

&#x20; border-radius: 5px;

&#x20; font-size: 12px;

}

</style>



\# Pipeline Nextflow



<div class="section-box">

La pipeline <strong>Nextflow</strong> rappresenta il nucleo computazionale del sistema ClinicalTwin per il preprocessing neuroimaging e l’estrazione delle feature radiomiche da immagini MRI strutturali in formato <strong>NIfTI</strong>.

</div>



Essa implementa un workflow automatizzato composto da:



<ul>

<li>segmentazione anatomica cerebrale</li>

<li>generazione delle ROI</li>

<li>conversione volumi segmentati</li>

<li>estrazione feature radiomiche</li>

<li>costruzione dataset CSV</li>

</ul>



Pipeline eseguita dal servizio:



<span class="badge">nextflow\_worker</span>



tramite architettura <strong>Docker-out-of-Docker (DooD)</strong>.



\---



\# Workflow computazionale



<div class="pipeline-box">

MRI → FreeSurfer / FastSurfer → ROI extraction → NIfTI conversion → Radiomics extraction → CSV dataset

</div>



Workflow implementato nel file:



<span class="code-path">

nextflow\_worker/nextflow/preprocessing.nf

</span>



\---



\# Struttura della pipeline



<table>

<tr>

<th>Processo</th>

<th>Funzione</th>

</tr>



<tr>

<td><strong>freesurfer</strong></td>

<td>Segmentazione anatomica</td>

</tr>



<tr>

<td><strong>nifti\_converter</strong></td>

<td>Conversione volumi segmentati</td>

</tr>



<tr>

<td><strong>roi\_creator</strong></td>

<td>Creazione maschere ROI</td>

</tr>



<tr>

<td><strong>csv\_collector</strong></td>

<td>Aggregazione feature</td>

</tr>



<tr>

<td><strong>feature\_extraction</strong></td>

<td>Estrazione radiomica</td>

</tr>

</table>



\---



\# Segmentazione anatomica



Segmentatori disponibili:



<ul>

<li><strong>FreeSurfer</strong></li>

<li><strong>FastSurfer</strong></li>

</ul>



Configurazione segmentatore:



<span class="code-path">

nextflow\_worker/nextflow/configs/nextflow.config

</span>



Parametro:



<pre>

params.brain\_segmenter = freesurfer

</pre>



Output generati:



<ul>

<li>volumetrie corticali</li>

<li>strutture sottocorticali</li>

<li>parcellazione anatomica standardizzata</li>

</ul>



\---



\# Generazione ROI



File di configurazione ROI:



<span class="code-path">

nextflow\_worker/data/external/ROI\_labels.tsv

</span>



Contiene:



<ul>

<li>etichette FreeSurfer</li>

<li>ID numerici</li>

<li>mapping anatomico</li>

</ul>



Totale ROI utilizzate:



<div class="pipeline-box">

78 regioni cerebrali

</div>



\---



\# Conversione volumi segmentati



Processo:



<span class="badge">nifti\_converter</span>



Operazioni principali:



<ul>

<li>selezione ROI</li>

<li>generazione maschere binarie</li>

<li>normalizzazione formato</li>

</ul>



Output prodotto:



<pre>

ROI\_mask.nii.gz

</pre>



\---



\# Estrazione feature radiomiche



Estrazione eseguita tramite:



<span class="badge">PyRadiomics</span>



Configurazione:



<span class="code-path">

nextflow\_worker/data/external/pyradiomics.yaml

</span>



Feature estratte:



<h3>First-order statistics</h3>



<ul>

<li>mean</li>

<li>variance</li>

<li>skewness</li>

<li>kurtosis</li>

<li>entropy</li>

</ul>



<h3>Shape features</h3>



<ul>

<li>volume</li>

<li>surface area</li>

<li>compactness</li>

<li>sphericity</li>

</ul>



<h3>Texture features</h3>



<ul>

<li>GLCM</li>

<li>GLRLM</li>

<li>GLSZM</li>

<li>NGTDM</li>

<li>GLDM</li>

</ul>



\---



\# Generazione dataset CSV



Aggregazione feature tramite:



<span class="badge">csv\_collector</span>



Output finale:



<pre>

radiomics\_features.csv

</pre>



Contiene:



<ul>

<li>feature per ciascuna ROI</li>

<li>dataset tabellare ML-ready</li>

<li>input diretto per model\_service</li>

</ul>



\---



\# Parametri configurabili



File configurazione:



<span class="code-path">

nextflow\_worker/nextflow/configs/nextflow.config

</span>



<table>

<tr>

<th>Parametro</th>

<th>Descrizione</th>

</tr>



<tr>

<td>maxforks</td>

<td>numero massimo processi paralleli</td>

</tr>



<tr>

<td>fastsurfer\_threads</td>

<td>thread CPU FastSurfer</td>

</tr>



<tr>

<td>fastsurfer\_device</td>

<td>cpu / cuda</td>

</tr>



<tr>

<td>fastsurfer\_3T</td>

<td>ottimizzazione scanner 3T</td>

</tr>



<tr>

<td>pyradiomics\_jobs</td>

<td>parallelismo estrazione feature</td>

</tr>



<tr>

<td>brain\_segmenter</td>

<td>segmentatore selezionato</td>

</tr>

</table>



\---



\# Architettura Docker-out-of-Docker



Pipeline basata su:



<div class="pipeline-box">

Docker-out-of-Docker (DooD)

</div>



Significa che:



<ul>

<li>Nextflow gira dentro <strong>nextflow\_worker</strong></li>

<li>i container pipeline girano sull’host Docker</li>

<li>le immagini devono essere pre-costruite</li>

</ul>



Build immagini richieste:



<pre>

docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/

docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/

docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

</pre>



\---



\# Output della pipeline



<table>

<tr>

<th>Output</th>

<th>Descrizione</th>

</tr>



<tr>

<td>ROI masks</td>

<td>maschere anatomiche segmentate</td>

</tr>



<tr>

<td>radiomics\_features.csv</td>

<td>dataset feature radiomiche</td>

</tr>



<tr>

<td>Nextflow logs</td>

<td>tracciamento esecuzione</td>

</tr>

</table>



Il dataset CSV viene successivamente utilizzato dal <strong>model\_service</strong> per la classificazione nello spazio latente UMAP.

