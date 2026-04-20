<style>

.hero {

&#x20; border-left: 6px solid #3f51b5;

&#x20; background: #eef2ff;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}

.section {

&#x20; margin-top: 28px;

}

</style>



<h1>ClinicalTwin</h1>



<div class="hero">

ClinicalTwin è una piattaforma software modulare per l’analisi automatizzata di immagini MRI cerebrali strutturali finalizzata alla diagnosi differenziale della behavioral variant Frontotemporal Dementia (bvFTD).

</div>



<div class="section">

<h2>Obiettivo clinico</h2>



La piattaforma supporta la diagnosi differenziale tra:



<ul>

<li>Healthy Controls (HC)</li>

<li>behavioral variant Frontotemporal Dementia (bvFTD)</li>

</ul>



tramite analisi radiomica automatizzata e classificazione supervisionata basata su feature estratte da immagini MRI T1-weighted.

</div>



<div class="section">

<h2>Input MRI NIfTI</h2>



Formati supportati:



<ul>

<li>.nii</li>

<li>.nii.gz</li>

</ul>



Le immagini vengono processate automaticamente tramite pipeline FreeSurfer e PyRadiomics.

</div>



<div class="section">

<h2>Output diagnostico</h2>



Il sistema restituisce:



<ul>

<li>classe predetta (HC vs bvFTD)</li>

<li>probabilità diagnostica</li>

<li>coordinate UMAP</li>

<li>feature radiomiche estratte</li>

<li>metadati pipeline</li>

</ul>

</div>

