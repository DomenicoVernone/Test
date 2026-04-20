Pipeline neuroimaging

Panoramica del workflow



La pipeline neuroimaging implementata in ClinicalTwin consente la trasformazione automatizzata di immagini MRI strutturali T1-pesate in rappresentazioni quantitative utilizzabili per la classificazione diagnostica tra behavioral variant Frontotemporal Dementia (bvFTD) e Healthy Controls (HC).



Il workflow segue una sequenza strutturata di operazioni computazionali:



MRI → FreeSurfer → ROI → Radiomics → CSV → modello ML → UMAP



Ogni fase contribuisce alla costruzione progressiva di un vettore di biomarcatori radiomici interpretabili e riproducibili 



Input: immagini MRI strutturali



La pipeline riceve in ingresso immagini volumetriche cerebrali T1-pesate in formato NIfTI:



.nii

.nii.gz



Queste immagini rappresentano la base per l’estrazione di caratteristiche morfometriche regionali utilizzate nella classificazione diagnostica.



Prima dell’elaborazione, i dati vengono validati e organizzati per garantire compatibilità con la pipeline di segmentazione automatica.



Segmentazione anatomica con FreeSurfer



La prima fase della pipeline consiste nella segmentazione anatomica cerebrale tramite FreeSurfer, uno strumento ampiamente validato nel contesto della neuroimaging analysis.



Durante questa fase vengono eseguite:



normalizzazione spaziale dell’immagine;

rimozione del tessuto extracranico (skull stripping);

segmentazione delle strutture sottocorticali;

ricostruzione delle superfici corticali;

parcellizzazione della corteccia cerebrale.



Il risultato è una rappresentazione anatomica dettagliata del cervello suddivisa in regioni neuroanatomiche standardizzate.



Estrazione delle regioni di interesse (ROI)



Successivamente, la pipeline identifica un insieme predefinito di regioni di interesse (Regions of Interest, ROI) corrispondenti a strutture cerebrali rilevanti per l’analisi neurodegenerativa.



Le ROI vengono derivate dalle mappe di segmentazione prodotte da FreeSurfer e organizzate secondo atlanti neuroanatomici standard.



Questa fase consente di isolare le aree cerebrali su cui verranno calcolate le feature radiomiche.



Estrazione delle feature radiomiche



Una volta definite le ROI, viene eseguita l’estrazione delle feature radiomiche mediante strumenti dedicati.



Le feature radiomiche includono:



caratteristiche di intensità voxel-wise;

descrittori statistici di primo ordine;

metriche di texture;

caratteristiche morfologiche regionali.



Queste informazioni permettono di trasformare l’immagine MRI in una rappresentazione numerica ad alta dimensionalità utile per l’analisi computazionale 



Generazione del dataset strutturato (CSV)



Le feature estratte dalle ROI vengono aggregate in una rappresentazione tabellare strutturata in formato CSV, in cui:



ogni riga rappresenta un soggetto;

ogni colonna rappresenta una feature radiomica.



Questo dataset costituisce l’input del modello di classificazione supervisionata.



La standardizzazione del formato consente l’integrazione con moduli di inferenza indipendenti dalla pipeline di preprocessing.



Classificazione tramite modello di Machine Learning



Il vettore di feature radiomiche viene successivamente utilizzato da un modello di machine learning supervisionato addestrato per distinguere tra:



Healthy Control (HC)

behavioral variant Frontotemporal Dementia (bvFTD)



Il modello restituisce:



la classe predetta;

informazioni diagnostiche associate;

rappresentazioni latenti del soggetto nello spazio delle feature.



Questa fase rappresenta il nucleo decisionale del sistema di supporto diagnostico 



Proiezione nello spazio latente UMAP



Come fase finale della pipeline, i dati radiomici vengono proiettati in uno spazio latente tridimensionale tramite UMAP (Uniform Manifold Approximation and Projection).



Questa trasformazione consente di:



visualizzare la distribuzione dei soggetti nello spazio delle feature;

confrontare il profilo del paziente con quello della popolazione di riferimento;

facilitare l’interpretazione delle predizioni del modello;

supportare l’esplorazione interattiva dei risultati tramite l’interfaccia clinica.



La rappresentazione UMAP costituisce uno strumento di interpretabilità visiva particolarmente utile nel contesto del supporto decisionale assistito 

