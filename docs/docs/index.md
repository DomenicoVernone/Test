ClinicalTwin – Sistema per l’analisi automatizzata di immagini MRI nella diagnosi differenziale della bvFTD 
Cos’è ClinicalTwin

ClinicalTwin è una piattaforma software modulare progettata per supportare l’analisi automatizzata di immagini di risonanza magnetica cerebrale strutturale (MRI T1-pesata) nell’ambito della diagnosi differenziale delle patologie neurodegenerative.

Il sistema implementa una pipeline completa di elaborazione neuroimaging che integra tecniche di segmentazione anatomica cerebrale, estrazione di feature radiomiche e classificazione supervisionata tramite modelli di machine learning. L’architettura è basata su microservizi containerizzati orchestrati tramite Docker e workflow computazionali gestiti mediante Nextflow, garantendo elevati livelli di riproducibilità, scalabilità e portabilità dell’intero processo di analisi.

ClinicalTwin consente l’automazione dell’intero flusso di elaborazione, dalla ricezione dell’immagine MRI fino alla generazione della predizione diagnostica, rendendo il sistema adatto sia a contesti sperimentali sia a scenari di supporto decisionale clinico assistito.

Obiettivo clinico

L’obiettivo principale della piattaforma ClinicalTwin è supportare il processo di diagnosi differenziale tra soggetti sani (Healthy Controls, HC) e pazienti affetti da variante comportamentale della demenza frontotemporale (behavioral variant Frontotemporal Dementia, bvFTD) mediante l’analisi quantitativa di immagini MRI strutturali.

In particolare, il sistema consente di:

eseguire automaticamente la segmentazione anatomica cerebrale;
estrarre biomarcatori radiomici regionali dalle immagini MRI;
costruire vettori di feature quantitative ad alta dimensionalità;
applicare modelli di classificazione supervisionata per la predizione diagnostica;
supportare l’interpretazione dei risultati tramite strumenti di visualizzazione interattiva.

Questo approccio permette di integrare informazioni morfometriche oggettive nel processo diagnostico, contribuendo alla valutazione precoce e differenziale delle patologie neurodegenerative frontotemporali 

Input: immagini MRI in formato NIfTI

ClinicalTwin utilizza come input immagini di risonanza magnetica cerebrale strutturale T1-pesata nel formato standard NIfTI:

.nii
.nii.gz

Le immagini devono essere:

volumetriche tridimensionali (3D);
acquisite con sequenze T1-weighted ad alta risoluzione;
compatibili con la pipeline di segmentazione FreeSurfer;
preferibilmente organizzate secondo lo standard BIDS (Brain Imaging Data Structure).

Durante la fase di preprocessing, le immagini vengono sottoposte automaticamente alle seguenti operazioni:

segmentazione anatomica cerebrale tramite FreeSurfer;
identificazione delle regioni di interesse (ROI);
generazione delle maschere anatomiche regionali;
estrazione delle feature radiomiche mediante strumenti dedicati.

Questo processo consente la trasformazione dell’immagine MRI grezza in un vettore strutturato di biomarcatori quantitativi utilizzabili per l’analisi computazionale 

Output: predizione diagnostica bvFTD vs Healthy Control

Al termine della pipeline di elaborazione, ClinicalTwin restituisce una predizione diagnostica automatizzata del soggetto analizzato nello spazio decisionale del classificatore supervisionato:

Healthy Control (HC)
oppure
behavioral variant Frontotemporal Dementia (bvFTD)

La classificazione è basata su feature radiomiche estratte da regioni cerebrali segmentate automaticamente e successivamente analizzate mediante modelli di machine learning addestrati su dataset di riferimento.

Oltre alla predizione diagnostica finale, il sistema produce ulteriori informazioni di supporto, tra cui:

vettori di feature radiomiche estratte;
coordinate di proiezione nello spazio latente (UMAP);
stato di avanzamento del task di elaborazione;
metadati associati alla pipeline di preprocessing;
informazioni utili all’interpretazione clinica assistita.