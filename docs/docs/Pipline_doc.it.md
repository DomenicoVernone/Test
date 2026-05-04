<!DOCTYPE html>

<html lang="it">

<head>

&#x20;   <meta charset="UTF-8">

&#x20;   <title>Pipeline MLOps Radiomica</title>

&#x20;   <style>

&#x20;       body {

&#x20;           font-family: Arial, sans-serif;

&#x20;           line-height: 1.6;

&#x20;           margin: 40px;

&#x20;           background-color: #f9f9f9;

&#x20;           color: #333;

&#x20;       }



&#x20;       h1, h2, h3 {

&#x20;           color: #2c3e50;

&#x20;       }



&#x20;       h1 {

&#x20;           border-bottom: 2px solid #ccc;

&#x20;           padding-bottom: 10px;

&#x20;       }



&#x20;       pre {

&#x20;           background-color: #eee;

&#x20;           padding: 15px;

&#x20;           border-radius: 5px;

&#x20;           overflow-x: auto;

&#x20;       }



&#x20;       .section {

&#x20;           margin-bottom: 40px;

&#x20;       }



&#x20;       .box {

&#x20;           background-color: #ffffff;

&#x20;           padding: 20px;

&#x20;           border-radius: 8px;

&#x20;           box-shadow: 0 2px 6px rgba(0,0,0,0.1);

&#x20;       }



&#x20;       ul {

&#x20;           margin-left: 20px;

&#x20;       }

&#x20;   </style>

</head>

<body>



<div class="box">



<h1>📄 Pipeline MLOps per l’estrazione di feature radiomiche</h1>



<div class="section">

<h2>1. Introduzione</h2>

<p>

Nel contesto del sistema Clinical Twin, è stata progettata e implementata una pipeline automatizzata per il processamento di immagini di risonanza magnetica (MRI) cerebrale e l’estrazione di biomarcatori quantitativi.

La pipeline è realizzata mediante Nextflow e si inserisce all’interno di un’architettura distribuita a microservizi, con l’obiettivo di garantire riproducibilità, modularità e scalabilità secondo i principi dell’MLOps.

</p>

<p>

L’intero flusso consente di trasformare immagini MRI T1-weighted in un insieme strutturato di feature radiomiche, utilizzabili come input per modelli di inferenza clinica.

</p>

</div>



<div class="section">

<h2>2. Architettura generale della pipeline</h2>

<p>

La pipeline implementa una sequenza deterministica di operazioni, ciascuna incapsulata in un processo isolato e containerizzato.

</p>



<h3>Flusso logico:</h3>

<pre>

MRI (.nii)

&#x20;  ↓

Segmentazione cerebrale (FreeSurfer / FastSurfer)

&#x20;  ↓

Conversione in formato NIfTI

&#x20;  ↓

Estrazione ROI (Region of Interest)

&#x20;  ↓

Costruzione mapping per PyRadiomics

&#x20;  ↓

Estrazione feature radiomiche

&#x20;  ↓

Aggregazione finale

&#x20;  ↓

radiomics\_features.csv

</pre>



<p>

Il risultato finale è un file strutturato contenente feature quantitative per ciascuna regione cerebrale.

</p>

</div>



<div class="section">

<h2>3. Descrizione dei processi</h2>



<h3>3.1 Segmentazione cerebrale</h3>

<p>

Il primo step utilizza FreeSurfer oppure FastSurfer per eseguire la segmentazione anatomica del cervello.

</p>

<p>

Questo processo produce una parcellizzazione volumetrica in cui ogni voxel viene associato a una specifica regione cerebrale (es. ippocampo, amigdala, corteccia frontale).

L’output principale è il file aparc+aseg.mgz.

</p>



<h3>3.2 Conversione dei dati</h3>

<p>

I file generati da FreeSurfer sono in formato .mgz, non compatibile con gli strumenti radiomici.

Il processo nifti\_converter converte tali file in formato .nii, rendendoli utilizzabili dagli step successivi.

</p>



<h3>3.3 Estrazione delle ROI</h3>

<p>

Il processo roi\_creator, basato su FSL, genera maschere binarie per ciascuna regione cerebrale.

</p>



<pre>

ROI/

&#x20;├── hippocampus.nii.gz

&#x20;├── amygdala.nii.gz

&#x20;├── thalamus.nii.gz

</pre>



<p>

Questo step è fondamentale per isolare le singole strutture anatomiche su cui verranno calcolate le feature.

</p>



<h3>3.4 Preparazione dei dati per PyRadiomics</h3>

<p>

Il processo csv\_collector costruisce file CSV di mapping nel formato richiesto da PyRadiomics:

</p>



<pre>

Image,Mask

nu.nii,ROI/hippocampus.nii.gz

</pre>



<p>

Ogni file CSV rappresenta una specifica regione di interesse.

</p>



<h3>3.5 Estrazione delle feature radiomiche</h3>

<p>

Il processo feature\_extraction utilizza PyRadiomics per calcolare feature quantitative per ciascuna ROI.

</p>



<p>Le feature includono:</p>

<ul>

<li>statistiche di primo ordine (mean, variance, skewness)</li>

<li>caratteristiche di forma (volume, superficie)</li>

<li>feature di texture (GLCM, GLRLM, GLSZM)</li>

</ul>



<h3>3.6 Aggregazione finale</h3>

<p>

Le feature generate per ciascuna ROI vengono aggregate in un unico file:

</p>



<pre>radiomics\_features.csv</pre>



<p>

Questo file rappresenta una matrice in cui:

</p>

<ul>

<li>ogni riga corrisponde a un soggetto</li>

<li>ogni colonna rappresenta una feature radiomica specifica</li>

</ul>

</div>



<div class="section">

<h2>4. Scelte progettuali</h2>

<p>

La pipeline è stata progettata secondo principi MLOps per garantire robustezza e affidabilità.

</p>



<h3>4.1 Gestione degli errori</h3>

<p>

È stato adottato un approccio fail-fast, impostando:

</p>

<pre>errorStrategy = 'terminate'</pre>



<p>

Questo garantisce che la pipeline venga interrotta immediatamente in caso di errore, evitando la produzione di output inconsistenti.

</p>



<h3>4.2 Gestione dei channel</h3>

<p>

I file statici (come ROI\_labels.tsv) vengono gestiti tramite:

</p>

<pre>Channel.value()</pre>



<p>

Questa scelta evita duplicazioni e garantisce una distribuzione deterministica dei dati tra i processi.

</p>



<h3>4.3 Consistenza dei dati</h3>

<p>

Dopo operazioni di join tra channel, viene effettuata una normalizzazione delle tuple per assicurare l’allineamento corretto tra:

</p>

<ul>

<li>immagini</li>

<li>ROI</li>

<li>metadata</li>

</ul>



<h3>4.4 Controlli di validità</h3>

<p>

Sono stati introdotti controlli espliciti per verificare:

</p>

<ul>

<li>generazione effettiva delle ROI</li>

<li>produzione di feature radiomiche</li>

</ul>



<p>

In caso contrario, la pipeline viene terminata con errore.

</p>



<h3>4.5 Containerizzazione</h3>

<p>

Ogni processo viene eseguito in un container Docker dedicato, garantendo:

</p>

<ul>

<li>isolamento delle dipendenze</li>

<li>portabilità</li>

<li>riproducibilità</li>

</ul>

</div>



<div class="section">

<h2>5. Output della pipeline</h2>

<p>

L’output principale è il file:

</p>



<pre>radiomics\_features.csv</pre>



<p>

Questo file contiene feature radiomiche strutturate e rappresenta l’input per il sistema di inferenza clinica.

</p>

</div>



<div class="section">

<h2>6. Integrazione nel sistema Clinical Twin</h2>



<pre>

Nextflow pipeline

&#x20;  ↓

radiomics\_features.csv

&#x20;  ↓

model\_service (MLflow / DagsHub)

&#x20;  ↓

inference\_engine (R)

&#x20;  ↓

Predizione + UMAP

&#x20;  ↓

Frontend (visualizzazione clinica)

</pre>



<p>

In particolare, l’inference engine utilizza le feature per:

</p>

<ul>

<li>classificazione diagnostica</li>

<li>proiezione nello spazio latente tramite UMAP 3D</li>

</ul>

</div>



<div class="section">

<h2>7. Miglioramenti introdotti</h2>

<p>

Rispetto alla versione iniziale, sono stati introdotti diversi miglioramenti:

</p>



<ul>

<li>sostituzione di errorStrategy = ignore con terminate</li>

<li>miglior gestione dei channel per evitare inconsistenze</li>

<li>introduzione di controlli espliciti sulle ROI generate</li>

<li>eliminazione di errori silenziosi nella fase di feature extraction</li>

<li>maggiore robustezza nella gestione dei file e dei path</li>

</ul>



<p>

Questi interventi hanno trasformato la pipeline da prototipo sperimentale a componente affidabile in un sistema MLOps.

</p>

</div>



<div class="section">

<h2>8. Conclusioni</h2>

<p>

La pipeline sviluppata rappresenta un elemento centrale del sistema Clinical Twin, consentendo la trasformazione automatizzata di dati di imaging complessi in feature strutturate e interpretabili.

</p>



<p>

L’adozione di Nextflow e di un’architettura containerizzata permette di garantire elevati livelli di riproducibilità e scalabilità, rendendo la soluzione adatta a contesti clinici e di ricerca avanzata.

</p>

</div>



</div>



</body>

</html>

