<style>

.box {

&#x20; border-left: 6px solid #3f51b5;

&#x20; background: #eef2ff;

&#x20; padding: 14px;

&#x20; border-radius: 6px;

&#x20; margin: 18px 0;

}



.flow {

&#x20; background: #f5f6fa;

&#x20; font-family: monospace;

&#x20; text-align: center;

&#x20; padding: 12px;

&#x20; border-radius: 6px;

&#x20; margin: 18px 0;

}



.code {

&#x20; background: #eeeeee;

&#x20; padding: 4px 8px;

&#x20; border-radius: 4px;

&#x20; font-family: monospace;

}

</style>





<h1>Pipeline Neuroimaging</h1>





<div class="box">



La pipeline neuroimaging implementata in ClinicalTwin consente la trasformazione automatizzata di immagini MRI strutturali T1-pesate in rappresentazioni quantitative utilizzabili per la classificazione diagnostica tra <strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong> e <strong>Healthy Controls (HC)</strong>.



Ogni fase contribuisce alla costruzione progressiva di un vettore di biomarcatori radiomici interpretabili e riproducibili.



</div>





<h2>Workflow computazionale</h2>



<div class="flow">

MRI → FreeSurfer → ROI → Radiomics → CSV → Machine Learning → UMAP

</div>





<h2>Input: immagini MRI strutturali</h2>



La pipeline riceve in ingresso immagini volumetriche cerebrali T1-pesate in formato NIfTI:



<ul>

<li><code>.nii</code></li>

<li><code>.nii.gz</code></li>

</ul>



Queste immagini rappresentano la base per l’estrazione di caratteristiche morfometriche regionali utilizzate nella classificazione diagnostica.



Prima dell’elaborazione, i dati vengono validati e organizzati per garantire compatibilità con la pipeline di segmentazione automatica.





<h2>Segmentazione anatomica con FreeSurfer</h2>



La prima fase della pipeline consiste nella segmentazione anatomica cerebrale tramite FreeSurfer, uno strumento ampiamente validato nel contesto della neuroimaging analysis.



Durante questa fase vengono eseguite:



<ul>

<li>normalizzazione spaziale dell’immagine</li>

<li>rimozione del tessuto extracranico (skull stripping)</li>

<li>segmentazione delle strutture sottocorticali</li>

<li>ricostruzione delle superfici corticali</li>

<li>parcellizzazione della corteccia cerebrale</li>

</ul>



Il risultato è una rappresentazione anatomica dettagliata del cervello suddivisa in regioni neuroanatomiche standardizzate.





<h2>Estrazione delle regioni di interesse (ROI)</h2>



Successivamente, la pipeline identifica un insieme predefinito di regioni di interesse (Regions of Interest, ROI) corrispondenti a strutture cerebrali rilevanti per l’analisi neurodegenerativa.



Le ROI vengono derivate dalle mappe di segmentazione prodotte da FreeSurfer e organizzate secondo atlanti neuroanatomici standard.



Questa fase consente di isolare le aree cerebrali su cui verranno calcolate le feature radiomiche.





<h2>Radiomics extraction</h2>



Una volta definite le ROI, viene eseguita l’estrazione delle feature radiomiche mediante strumenti dedicati.



Le feature radiomiche includono:



<ul>

<li>caratteristiche di intensità voxel-wise</li>

<li>descrittori statistici di primo ordine</li>

<li>metriche di texture</li>

<li>caratteristiche morfologiche regionali</li>

</ul>



Queste informazioni permettono di trasformare l’immagine MRI in una rappresentazione numerica ad alta dimensionalità utile per l’analisi computazionale.





<h2>Generazione del dataset strutturato (CSV)</h2>



Le feature estratte dalle ROI vengono aggregate in una rappresentazione tabellare strutturata in formato CSV, in cui:



<ul>

<li>ogni riga rappresenta un soggetto</li>

<li>ogni colonna rappresenta una feature radiomica</li>

</ul>



Questo dataset costituisce l’input del modello di classificazione supervisionata.



La standardizzazione del formato consente l’integrazione con moduli di inferenza indipendenti dalla pipeline di preprocessing.





<h2>Classificazione tramite modello di Machine Learning</h2>



Il vettore di feature radiomiche viene successivamente utilizzato da un modello di machine learning supervisionato addestrato per distinguere tra:



<ul>

<li>Healthy Control (HC)</li>

<li>behavioral variant Frontotemporal Dementia (bvFTD)</li>

</ul>



Il modello restituisce:



<ul>

<li>classe predetta</li>

<li>informazioni diagnostiche associate</li>

<li>rappresentazioni latenti del soggetto nello spazio delle feature</li>

</ul>



Questa fase rappresenta il nucleo decisionale del sistema di supporto diagnostico.





<h2>Proiezione nello spazio latente UMAP</h2>



Come fase finale della pipeline, i dati radiomici vengono proiettati in uno spazio latente tridimensionale tramite UMAP (Uniform Manifold Approximation and Projection).



Questa trasformazione consente di:



<ul>

<li>visualizzare la distribuzione dei soggetti nello spazio delle feature</li>

<li>confrontare il profilo del paziente con quello della popolazione di riferimento</li>

<li>facilitare l’interpretazione delle predizioni del modello</li>

<li>supportare l’esplorazione interattiva dei risultati tramite l’interfaccia clinica</li>

</ul>



La rappresentazione UMAP costituisce uno strumento di interpretabilità visiva particolarmente utile nel contesto del supporto decisionale assistito.

