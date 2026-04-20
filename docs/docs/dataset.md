<style>

.dataset-box {

&#x20; border-left: 6px solid #4caf50;

&#x20; background: #edf7ed;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

}

</style>



<h1>Dataset MRI</h1>



<div class="dataset-box">

ClinicalTwin utilizza immagini MRI strutturali in formato NIfTI come input della pipeline radiomica.

</div>



<h2>Formato supportato</h2>



<ul>

<li>.nii</li>

<li>.nii.gz</li>

</ul>



Contengono:



<ul>

<li>intensità voxel-wise</li>

<li>orientamento anatomico</li>

<li>voxel spacing</li>

<li>metadati acquisizione</li>

</ul>



<h2>Preprocessing automatico</h2>



Operazioni eseguite:



<ul>

<li>normalizzazione orientamento</li>

<li>skull stripping</li>

<li>segmentazione tessuti</li>

<li>ricostruzione superfici corticali</li>

<li>parcellizzazione anatomica</li>

</ul>



<h2>ROI extraction</h2>



Numero ROI:



<strong>78 regioni cerebrali</strong>



derivate da atlanti FreeSurfer.



<h2>Radiomics extraction</h2>



Feature estratte:



<ul>

<li>first-order statistics</li>

<li>texture descriptors</li>

<li>shape features</li>

</ul>



Output finale:



<code>radiomics\_features.csv</code>

