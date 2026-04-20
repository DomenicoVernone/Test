<style>

.model-box {

&#x20; border-left: 6px solid #ff9800;

&#x20; background: #fff7e6;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

}

</style>



<h1>Modelli di Machine Learning</h1>



<div class="model-box">

ClinicalTwin utilizza modelli supervisionati per classificare soggetti HC vs bvFTD.

</div>



<h2>Input modello</h2>



Dataset:



<code>radiomics\_features.csv</code>



Contiene feature estratte da:



<strong>78 ROI cerebrali</strong>



<h2>Algoritmo utilizzato</h2>



Classificatore:



<strong>K-Nearest Neighbors (KNN)</strong>



Vantaggi:



<ul>

<li>interpretabilità locale</li>

<li>assenza ipotesi parametriche</li>

<li>preservazione struttura geometrica feature space</li>

</ul>



<h2>Riduzione dimensionale</h2>



Tecnica:



<strong>UMAP</strong>



Permette:



<ul>

<li>visualizzazione spazio latente</li>

<li>identificazione cluster diagnostici</li>

<li>supporto interpretativo clinico</li>

</ul>



<h2>Model Registry</h2>



Gestione tramite:



<strong>MLflow + DagsHub</strong>



Supporta:



<ul>

<li>versionamento modelli</li>

<li>tracking esperimenti</li>

<li>selezione champion model</li>

</ul>

