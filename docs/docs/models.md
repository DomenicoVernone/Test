<style>

.model-box {

&#x20; border-left: 6px solid #ff9800;

&#x20; background: #fff7e6;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}



.code {

&#x20; font-family: monospace;

&#x20; background: #eeeeee;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; white-space: pre;

}

</style>





<h1>Modelli di Machine Learning</h1>





<div class="model-box">



Il sistema ClinicalTwin utilizza modelli di machine learning supervisionato per la diagnosi differenziale tra:



<ul>

<li>Healthy Controls (HC)</li>

<li>behavioral variant Frontotemporal Dementia (bvFTD)</li>

</ul>



I modelli operano su feature radiomiche estratte automaticamente da immagini MRI strutturali tramite pipeline FreeSurfer/FastSurfer + PyRadiomics.



</div>





<h2>Dataset di input</h2>



I modelli ricevono in ingresso un dataset tabellare:



<div class="code">

radiomics\_features.csv

</div>



contenente:



<ul>

<li>feature radiomiche per ciascuna ROI</li>

<li>statistiche di primo ordine</li>

<li>descrittori morfologici</li>

<li>feature di texture multiscala</li>

</ul>



Le feature sono estratte da:



<strong>78 regioni anatomiche cerebrali (ROI)</strong>



derivate dalla parcellazione FreeSurfer.





<h2>Pipeline di classificazione</h2>



Il workflow di inferenza segue la sequenza:



<div class="code">

Radiomics CSV → preprocessing → classificatore → probabilità diagnostica → embedding UMAP

</div>



Il risultato finale comprende:



<ul>

<li>classe predetta (HC vs bvFTD)</li>

<li>confidenza predittiva</li>

<li>coordinate nello spazio latente UMAP 3D</li>

</ul>





<h2>Algoritmo di classificazione</h2>



Il motore statistico implementato nel servizio <strong>inference\_engine</strong> utilizza un classificatore:



<strong>K-Nearest Neighbors (KNN)</strong>



Questo approccio è particolarmente adatto in contesti radiomici perché:



<ul>

<li>non assume distribuzioni parametriche</li>

<li>preserva la struttura geometrica dello spazio delle feature</li>

<li>consente interpretabilità locale</li>

<li>facilita la visualizzazione nello spazio latente</li>

</ul>



La distanza tra osservazioni viene calcolata nello spazio delle feature radiomiche normalizzate.





<h2>Riduzione dimensionale con UMAP</h2>



Per supportare l’interpretabilità clinica del risultato, il sistema utilizza:



<strong>UMAP (Uniform Manifold Approximation and Projection)</strong>



UMAP consente di:



<ul>

<li>ridurre dimensionalità dello spazio radiomico</li>

<li>preservare relazioni topologiche locali</li>

<li>rappresentare pazienti in uno spazio latente 3D</li>

<li>visualizzare cluster diagnostici</li>

</ul>



L’embedding risultante viene mostrato nella dashboard React tramite grafici interattivi Plotly.



Ogni nuovo paziente viene proiettato nello spazio latente rispetto al dataset di riferimento.





<h2>Model Registry con MLflow</h2>



La gestione dei modelli è affidata al servizio:



<strong>model\_service</strong>



che utilizza:



<strong>MLflow Model Registry (DagsHub backend)</strong>



Questo consente:



<ul>

<li>versionamento automatico dei modelli</li>

<li>tracciamento esperimenti</li>

<li>selezione dinamica del modello champion</li>

<li>riproducibilità delle predizioni</li>

<li>aggiornamento dinamico senza modifiche al codice</li>

</ul>





<h2>Variabili principali di configurazione</h2>



<div class="code">

MLFLOW\_TRACKING\_URI

MLFLOW\_TRACKING\_USERNAME

DAGSHUB\_TOKEN

REPO\_OWNER

REPO\_NAME

</div>





<h2>Selezione del modello champion</h2>



Durante l’inferenza, il sistema:



<ul>

<li>interroga MLflow</li>

<li>recupera il modello marcato come champion</li>

<li>scarica automaticamente la versione attiva</li>

<li>esegue la classificazione sul dataset radiomico</li>

</ul>



Questo approccio permette l’aggiornamento continuo delle prestazioni diagnostiche senza interrompere il servizio.





<h2>Output del modello</h2>



Il risultato dell’inferenza è restituito come struttura JSON:



<div class="code">

{

&#x20; "prediction": "bvFTD",

&#x20; "confidence": 0.82,

&#x20; "umap\_coordinates": \[1.24, -0.31, 2.08]

}

</div>



Include:



<ul>

<li><strong>prediction</strong> — classe diagnostica stimata</li>

<li><strong>confidence</strong> — probabilità associata</li>

<li><strong>umap\_coordinates</strong> — posizione nello spazio latente</li>

</ul>



Queste informazioni vengono visualizzate nella dashboard clinica e utilizzate dall’assistente LLM per generare spiegazioni contestuali.





<h2>Integrazione con assistente AI</h2>



I risultati del modello vengono trasmessi al servizio:



<strong>llm\_service</strong>



che utilizza un approccio:



<strong>Spatial RAG (Retrieval-Augmented Generation)</strong>



per integrare:



<ul>

<li>coordinate UMAP</li>

<li>cluster diagnostici</li>

<li>profilo radiomico del paziente</li>

</ul>



nelle risposte generate per il medico.



Questo consente interpretazioni clinicamente assistite e contestualizzate rispetto allo spazio latente del dataset.

