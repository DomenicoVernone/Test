<style>

.info-box {

&#x20; border-left: 6px solid #2962ff;

&#x20; background: #eef3ff;

&#x20; padding: 14px;

&#x20; margin: 18px 0;

&#x20; border-radius: 6px;

}



.pipeline-flow {

&#x20; background: #f4f6fa;

&#x20; padding: 14px;

&#x20; text-align: center;

&#x20; font-family: monospace;

&#x20; border-radius: 8px;

&#x20; font-size: 15px;

&#x20; margin: 20px 0;

}



.code-inline {

&#x20; background: #ececec;

&#x20; padding: 3px 8px;

&#x20; border-radius: 4px;

&#x20; font-family: monospace;

}



.badge {

&#x20; display: inline-block;

&#x20; background: #2962ff;

&#x20; color: white;

&#x20; padding: 4px 10px;

&#x20; border-radius: 5px;

&#x20; font-size: 12px;

}



.section-title {

&#x20; margin-top: 40px;

&#x20; border-bottom: 2px solid #e0e0e0;

&#x20; padding-bottom: 5px;

}



table {

&#x20; border-collapse: collapse;

&#x20; width: 100%;

&#x20; margin-top: 15px;

}



th {

&#x20; background: #f2f2f2;

}



th, td {

&#x20; padding: 10px;

&#x20; border: 1px solid #ddd;

}

</style>





<h1>Pipeline Nextflow</h1>



<div class="info-box">

La pipeline <strong>Nextflow</strong> rappresenta il nucleo computazionale del sistema ClinicalTwin per il preprocessing neuroimaging e l’estrazione automatizzata delle feature radiomiche da immagini MRI strutturali in formato <strong>NIfTI</strong>.

</div>





<h2 class="section-title">Workflow computazionale</h2>



<div class="pipeline-flow">

MRI → FreeSurfer / FastSurfer → ROI extraction → NIfTI conversion → Radiomics extraction → CSV dataset

</div>



Workflow implementato nel file:



<div class="code-inline">

nextflow\_worker/nextflow/preprocessing.nf

</div>





<h2 class="section-title">Struttura della pipeline</h2>



<table>

<tr>

<th>Processo</th>

<th>Funzione</th>

</tr>



<tr>

<td><strong>freesurfer</strong></td>

<td>Segmentazione anatomica cerebrale</td>

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

<td>Aggregazione feature radiomiche</td>

</tr>



<tr>

<td><strong>feature\_extraction</strong></td>

<td>Estrazione radiomica tramite PyRadiomics</td>

</tr>



</table>





<h2 class="section-title">Segmentazione anatomica</h2>



Segmentatori disponibili:



<ul>

<li>FreeSurfer</li>

<li>FastSurfer</li>

</ul>



Configurazione segmentatore:



<div class="code-inline">

nextflow\_worker/nextflow/configs/nextflow.config

</div>



Parametro:



<pre>

params.brain\_segmenter = "freesurfer"

</pre>



Output generati:



<ul>

<li>volumetrie corticali</li>

<li>strutture sottocorticali</li>

<li>parcellazione anatomica standardizzata</li>

</ul>





<h2 class="section-title">Generazione ROI</h2>



File configurazione ROI:



<div class="code-inline">

nextflow\_worker/data/external/ROI\_labels.tsv

</div>



Contiene:



<ul>

<li>etichette FreeSurfer</li>

<li>identificatori numerici</li>

<li>mapping anatomico</li>

</ul>



Numero totale ROI:



<div class="pipeline-flow">

78 regioni cerebrali

</div>





<h2 class="section-title">Conversione volumi segmentati</h2>



Processo:



<span class="badge">nifti\_converter</span>



Operazioni:



<ul>

<li>selezione ROI</li>

<li>generazione maschere binarie</li>

<li>normalizzazione formato</li>

</ul>



Output:



<pre>

ROI\_mask.nii.gz

</pre>





<h2 class="section-title">Estrazione feature radiomiche</h2>



Estrazione eseguita tramite:



<span class="badge">PyRadiomics</span>



Configurazione:



<div class="code-inline">

nextflow\_worker/data/external/pyradiomics.yaml

</div>





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





<h2 class="section-title">Generazione dataset CSV</h2>



Processo:



<span class="badge">csv\_collector</span>



Output finale:



<pre>

radiomics\_features.csv

</pre>



Contiene:



<ul>

<li>feature per ciascuna ROI</li>

<li>dataset compatibile con pipeline ML</li>

<li>input diretto per model\_service</li>

</ul>





<h2 class="section-title">Parametri configurabili</h2>



File configurazione:



<div class="code-inline">

nextflow\_worker/nextflow/configs/nextflow.config

</div>



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





<h2 class="section-title">Architettura Docker-out-of-Docker</h2>



<div class="pipeline-flow">

Docker-out-of-Docker (DooD)

</div>



Significa che:



<ul>

<li>Nextflow gira dentro <strong>nextflow\_worker</strong></li>

<li>i container pipeline girano sull’host Docker</li>

<li>le immagini devono essere pre-costruite localmente</li>

</ul>



Build immagini richieste:



<pre>

docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/



docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/



docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

</pre>





<h2 class="section-title">Output della pipeline</h2>



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

<td>tracciamento esecuzione pipeline</td>

</tr>



</table>



Il dataset CSV viene successivamente utilizzato dal <strong>model\_service</strong> per la classificazione diagnostica nello spazio latente <strong>UMAP</strong>.

