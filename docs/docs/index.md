<style>

.hero {

&#x20; border-left: 6px solid #3f51b5;

&#x20; background: #eef2ff;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 20px 0;

}



.section {

&#x20; border-left: 6px solid #009688;

&#x20; background: #eefaf8;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

&#x20; margin: 28px 0;

}

</style>





<h1>ClinicalTwin – Sistema per l’analisi automatizzata di immagini MRI nella diagnosi differenziale della bvFTD</h1>





<div class="hero">



ClinicalTwin è una piattaforma software modulare progettata per supportare l’analisi automatizzata di immagini di risonanza magnetica cerebrale strutturale (MRI T1-pesata) nell’ambito della diagnosi differenziale delle patologie neurodegenerative.



Il sistema implementa una pipeline completa di elaborazione neuroimaging che integra tecniche di segmentazione anatomica cerebrale, estrazione di feature radiomiche e classificazione supervisionata tramite modelli di machine learning. L’architettura è basata su microservizi containerizzati orchestrati tramite Docker e workflow computazionali gestiti mediante Nextflow, garantendo elevati livelli di riproducibilità, scalabilità e portabilità dell’intero processo di analisi.



ClinicalTwin consente l’automazione dell’intero flusso di elaborazione, dalla ricezione dell’immagine MRI fino alla generazione della predizione diagnostica, rendendo il sistema adatto sia a contesti sperimentali sia a scenari di supporto decisionale clinico assistito.



</div>





<h2>Cos’è ClinicalTwin</h2>



ClinicalTwin è una piattaforma software modulare per l’analisi automatizzata di immagini MRI cerebrali strutturali finalizzata alla diagnosi differenziale della behavioral variant Frontotemporal Dementia (bvFTD).



Il sistema integra:



<ul>

<li>segmentazione anatomica cerebrale automatizzata</li>

<li>estrazione di biomarcatori radiomici regionali</li>

<li>costruzione di vettori di feature quantitative ad alta dimensionalità</li>

<li>classificazione supervisionata tramite modelli di machine learning</li>

<li>strumenti di visualizzazione interattiva per l’interpretazione dei risultati</li>

</ul>





<div class="section">



<h2>Obiettivo clinico</h2>



L’obiettivo principale della piattaforma ClinicalTwin è supportare il processo di diagnosi differenziale tra:



<ul>

<li>Healthy Controls (HC)</li>

<li>behavioral variant Frontotemporal Dementia (bvFTD)</li>

</ul>



mediante l’analisi quantitativa di immagini MRI strutturali.



Questo approccio permette di integrare informazioni morfometriche oggettive nel processo diagnostico, contribuendo alla valutazione precoce e differenziale delle patologie neurodegenerative frontotemporali.



</div>





<div class="section">



<h2>Input MRI in formato NIfTI</h2>



ClinicalTwin utilizza come input immagini di risonanza magnetica cerebrale strutturale T1-pesata nel formato standard NIfTI:



<ul>

<li>.nii</li>

<li>.nii.gz</li>

</ul>



Le immagini devono essere:



<ul>

<li>volumetriche tridimensionali (3D)</li>

<li>acquisite con sequenze T1-weighted ad alta risoluzione</li>

<li>compatibili con la pipeline di segmentazione FreeSurfer</li>

<li>preferibilmente organizzate secondo lo standard BIDS (Brain Imaging Data Structure)</li>

</ul>



Durante la fase di preprocessing, le immagini vengono sottoposte automaticamente alle seguenti operazioni:



<ul>

<li>segmentazione anatomica cerebrale tramite FreeSurfer</li>

<li>identificazione delle regioni di interesse (ROI)</li>

<li>generazione delle maschere anatomiche regionali</li>

<li>estrazione delle feature radiomiche mediante strumenti dedicati</li>

</ul>



Questo processo consente la trasformazione dell’immagine MRI grezza in un vettore strutturato di biomarcatori quantitativi utilizzabili per l’analisi computazionale.



</div>





<div class="section">



<h2>Output diagnostico</h2>



Al termine della pipeline di elaborazione, ClinicalTwin restituisce una predizione diagnostica automatizzata del soggetto analizzato nello spazio decisionale del classificatore supervisionato:



<ul>

<li>classe predetta (Healthy Control vs bvFTD)</li>

<li>probabilità diagnostica</li>

<li>coordinate di proiezione nello spazio latente (UMAP)</li>

<li>feature radiomiche estratte</li>

<li>metadati associati alla pipeline di preprocessing</li>

<li>stato di avanzamento del task di elaborazione</li>

</ul>



La classificazione è basata su feature radiomiche estratte da regioni cerebrali segmentate automaticamente e successivamente analizzate mediante modelli di machine learning addestrati su dataset di riferimento.



Oltre alla predizione diagnostica finale, il sistema produce ulteriori informazioni utili all’interpretazione clinica assistita.



</div>

