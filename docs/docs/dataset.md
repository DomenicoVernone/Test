Dataset

Formato dei dati MRI: NIfTI



La piattaforma ClinicalTwin utilizza immagini di risonanza magnetica strutturale cerebrale in formato NIfTI (Neuroimaging Informatics Technology Initiative), che rappresenta lo standard de facto per la memorizzazione e la condivisione di dati neuroimaging tridimensionali.



I formati supportati includono:



.nii

.nii.gz



Il formato NIfTI consente la rappresentazione compatta di volumi MRI tridimensionali contenenti:



intensità voxel-wise;

informazioni spaziali (voxel spacing);

orientamento anatomico;

metadati associati all’acquisizione.



Per l’utilizzo all’interno della pipeline ClinicalTwin, le immagini devono essere acquisite tramite sequenze T1-weighted ad alta risoluzione, generalmente impiegate nello studio delle alterazioni morfostrutturali associate alle patologie neurodegenerative 🧠



Preprocessing richiesto



Le immagini MRI fornite in input vengono sottoposte automaticamente a una pipeline di preprocessing neuroanatomico basata su strumenti standardizzati di neuroimaging.



Le principali operazioni includono:



normalizzazione dell’orientamento spaziale;

rimozione del tessuto extracranico (skull stripping);

segmentazione dei tessuti cerebrali;

ricostruzione delle superfici corticali;

parcellizzazione anatomica regionale.



Queste operazioni sono eseguite tramite FreeSurfer, che consente di ottenere una rappresentazione strutturata e riproducibile dell’anatomia cerebrale del soggetto.



Non è richiesto preprocessing manuale preliminare da parte dell’utente, purché:



l’immagine sia completa;

non presenti artefatti severi;

sia acquisita con sequenza T1 strutturale standard.



Questo approccio garantisce uniformità nella generazione delle feature tra soggetti diversi 🔬



Estrazione delle regioni di interesse (ROI)



Dopo la segmentazione anatomica, la pipeline identifica automaticamente un insieme di regioni di interesse (Regions of Interest, ROI) corrispondenti a strutture cerebrali corticali e sottocorticali rilevanti per la classificazione diagnostica.



Le ROI vengono derivate da atlanti neuroanatomici standard integrati nella pipeline FreeSurfer e comprendono:



regioni frontali;

regioni temporali;

strutture limbiche;

strutture sottocorticali profonde.



Queste regioni rappresentano aree particolarmente informative nello studio della behavioral variant Frontotemporal Dementia (bvFTD), caratterizzata da alterazioni morfologiche selettive nei lobi frontali e temporali.



L’estrazione delle ROI consente di isolare sottovolumi anatomici specifici sui quali vengono successivamente calcolate le feature radiomiche 📊



Estrazione delle feature radiomiche



A partire dalle ROI segmentate, la pipeline esegue l’estrazione automatica di feature radiomiche quantitative tramite strumenti dedicati (PyRadiomics).



Le feature estratte includono diverse categorie descrittive:



Feature di primo ordine



Descrivono la distribuzione statistica delle intensità voxel all’interno della ROI:



media

varianza

skewness

kurtosis

entropia

Feature di texture



Caratterizzano la struttura spaziale delle intensità voxel:



Gray Level Co-occurrence Matrix (GLCM)

Gray Level Run Length Matrix (GLRLM)

Gray Level Size Zone Matrix (GLSZM)

Neighboring Gray Tone Difference Matrix (NGTDM)



Queste metriche consentono di catturare pattern microstrutturali non osservabili visivamente.



Feature morfologiche



Descrivono proprietà geometriche delle regioni segmentate:



volume regionale

superficie

compattezza

sfericità

rapporti dimensionali principali



Queste caratteristiche risultano particolarmente rilevanti nello studio dell’atrofia regionale associata alla degenerazione frontotemporale.



Dataset radiomico finale



Le feature estratte vengono aggregate in un dataset strutturato in formato CSV, in cui:



ogni riga rappresenta un soggetto;

ogni colonna rappresenta una feature radiomica;

ogni ROI contribuisce con un insieme specifico di descrittori quantitativi.



Questo dataset costituisce l’input del modello di classificazione supervisionata utilizzato per la distinzione tra:



Healthy Control (HC)

behavioral variant Frontotemporal Dementia (bvFTD)



La trasformazione delle immagini MRI in rappresentazioni numeriche ad alta dimensionalità consente l’applicazione di metodi avanzati di machine learning per il supporto decisionale clinico assistito 🧬

