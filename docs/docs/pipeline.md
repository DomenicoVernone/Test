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

La pipeline neuroimaging ClinicalTwin consente la trasformazione automatizzata di immagini MRI T1-pesate in biomarcatori quantitativi per la classificazione diagnostica tra <strong>bvFTD</strong> e <strong>Healthy Controls</strong>.

</div>



<h2>Workflow computazionale</h2>



<div class="flow">

MRI → FreeSurfer → ROI → Radiomics → CSV → Machine Learning → UMAP

</div>



<h2>Input MRI strutturali</h2>



Formati supportati:



<ul>

<li>.nii</li>

<li>.nii.gz</li>

</ul>



Le immagini vengono validate prima dell’elaborazione per garantire compatibilità con la pipeline.



<h2>Segmentazione anatomica</h2>



Segmentazione eseguita tramite:



<ul>

<li>normalizzazione spaziale</li>

<li>skull stripping</li>

<li>segmentazione sottocorticale</li>

<li>ricostruzione superfici corticali</li>

<li>parcellizzazione anatomica</li>

</ul>



<h2>Estrazione ROI</h2>



Le ROI sono derivate da atlanti neuroanatomici standard e rappresentano regioni rilevanti per l’analisi neurodegenerativa.



<h2>Radiomics extraction</h2>



Feature estratte:



<ul>

<li>statistiche voxel-wise</li>

<li>first-order features</li>

<li>texture descriptors</li>

<li>shape features</li>

</ul>



<h2>Dataset CSV</h2>



Struttura:



<ul>

<li>righe → soggetti</li>

<li>colonne → feature radiomiche</li>

</ul>



Utilizzato come input del classificatore diagnostico.



<h2>Classificazione ML</h2>



Output modello:



<ul>

<li>classe predetta</li>

<li>probabilità diagnostica</li>

<li>embedding latente</li>

</ul>



<h2>Proiezione UMAP</h2>



Consente:



<ul>

<li>visualizzazione distribuzione soggetti</li>

<li>confronto con dataset di riferimento</li>

<li>supporto interpretativo clinico</li>

</ul>

