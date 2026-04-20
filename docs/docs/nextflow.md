Pipeline Nextflow

Panoramica generale



La pipeline Nextflow costituisce il nucleo computazionale del sistema ClinicalTwin per il preprocessing neuroimaging e l’estrazione delle feature radiomiche a partire da immagini MRI strutturali in formato NIfTI.



Essa implementa un workflow completamente automatizzato che comprende:



segmentazione anatomica cerebrale

generazione delle regioni di interesse (ROI)

conversione dei volumi segmentati

estrazione delle feature radiomiche

costruzione del dataset finale per classificazione



La pipeline è eseguita dal servizio nextflow\_worker tramite architettura Docker-out-of-Docker (DooD).



Workflow computazionale



Il flusso operativo della pipeline è il seguente:



MRI → FreeSurfer / FastSurfer → ROI extraction → NIfTI conversion → Radiomics extraction → CSV dataset



Ogni fase è implementata come processo indipendente nel file:



nextflow\_worker/nextflow/preprocessing.nf

Struttura della pipeline



La pipeline Nextflow è composta dai seguenti moduli principali:



Processo	Funzione

freesurfer	Segmentazione anatomica

nifti\_converter	Conversione volumi segmentati

roi\_creator	Creazione maschere ROI

csv\_collector	Aggregazione feature

feature\_extraction	Estrazione radiomica



Ogni processo è containerizzato tramite immagini Docker dedicate.



Segmentazione anatomica



La segmentazione cerebrale viene eseguita utilizzando uno dei due segmentatori disponibili:



FreeSurfer

FastSurfer



Il segmentatore attivo è configurabile tramite:



nextflow\_worker/nextflow/configs/nextflow.config



Parametro:



params.brain\_segmenter = freesurfer



Output della segmentazione:



volumetrie corticali

strutture sottocorticali

parcellazione anatomica standardizzata

Generazione ROI



Le regioni di interesse sono definite tramite:



nextflow\_worker/data/external/ROI\_labels.tsv



Il file contiene:



etichette FreeSurfer

identificatori numerici

mapping anatomico



Numero totale ROI:



78 regioni cerebrali



Le ROI costituiscono l’input per l’estrazione delle feature radiomiche.



Conversione volumi segmentati



Il processo nifti\_converter trasforma i volumi segmentati nel formato compatibile con PyRadiomics.



Operazioni principali:



selezione ROI

generazione maschere binarie

normalizzazione formato



Output:



ROI\_mask.nii.gz



per ciascuna regione anatomica.



Estrazione feature radiomiche



L’estrazione radiomica è eseguita tramite PyRadiomics utilizzando il file di configurazione:



nextflow\_worker/data/external/pyradiomics.yaml



Feature estratte:



First-order statistics



Descrivono la distribuzione dell’intensità voxel:



mean

variance

skewness

kurtosis

entropy

Shape features



Descrivono la morfologia della ROI:



volume

surface area

compactness

sphericity

Texture features



Derivate da matrici statistiche spaziali:



GLCM

GLRLM

GLSZM

NGTDM

GLDM



Queste feature rappresentano biomarcatori quantitativi della struttura cerebrale.



Generazione dataset CSV



Le feature radiomiche vengono aggregate nel processo:



csv\_collector



Output finale:



radiomics\_features.csv



Il file contiene:



feature per ciascuna ROI

struttura tabellare compatibile con pipeline ML

input diretto per model\_service

Parametri configurabili



I parametri principali della pipeline sono definiti in:



nextflow\_worker/nextflow/configs/nextflow.config



Parametri principali:



Parametro	Descrizione

maxforks	numero massimo processi paralleli

fastsurfer\_threads	thread CPU FastSurfer

fastsurfer\_device	device (cpu / cuda)

fastsurfer\_3T	ottimizzazione scanner 3T

pyradiomics\_jobs	parallelismo estrazione feature

brain\_segmenter	segmentatore selezionato



Questa configurazione consente l’adattamento della pipeline a diversi ambienti hardware.



Architettura Docker-out-of-Docker



La pipeline utilizza il paradigma:



Docker-out-of-Docker (DooD)



In questo approccio:



Nextflow gira dentro il container nextflow\_worker

i processi della pipeline vengono eseguiti dal Docker host

le immagini pipeline devono essere pre-costruite localmente



Immagini richieste:



clinical-freesurfer

clinical-fsl

clinical-pyradiomics



Costruzione:



docker build -t clinical-freesurfer -f nextflow\_worker/freesurfer.dockerfile nextflow\_worker/

docker build -t clinical-fsl -f nextflow\_worker/fsl.dockerfile nextflow\_worker/

docker build -t clinical-pyradiomics -f nextflow\_worker/pyradiomics.dockerfile nextflow\_worker/

Output della pipeline



Al termine dell’elaborazione, la pipeline produce:



Output	Descrizione

ROI masks	maschere anatomiche segmentate

radiomics\_features.csv	dataset feature radiomiche

log Nextflow	tracciamento esecuzione



Il dataset CSV viene successivamente utilizzato dal model\_service per la classificazione diagnostica nello spazio latente UMAP.

