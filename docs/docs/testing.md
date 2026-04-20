<style>

.testbox {

&#x20; border-left: 6px solid #4caf50;

&#x20; background: #edf7ed;

&#x20; padding: 14px;

&#x20; margin: 16px 0;

&#x20; border-radius: 6px;

}



.code {

&#x20; font-family: monospace;

&#x20; background: #eeeeee;

&#x20; padding: 10px;

&#x20; border-radius: 6px;

&#x20; white-space: pre;

}

</style>





<h1>Testing</h1>





<div class="testbox">



Questa sezione descrive le procedure di verifica funzionale dei principali componenti della piattaforma ClinicalTwin, al fine di garantire il corretto funzionamento dello stack applicativo e della pipeline di analisi neuroimaging.



Le attività di testing includono:



<ul>

<li>verifica dei container Docker</li>

<li>test della pipeline Nextflow</li>

<li>validazione del classificatore diagnostico</li>

<li>test della dashboard clinica</li>

</ul>



</div>





<h2>Test container Docker</h2>



Dopo l’avvio dello stack applicativo, verificare che tutti i servizi risultino attivi:



<div class="code">

docker compose ps

</div>



Devono risultare in stato <strong>running</strong> i seguenti container:



<ul>

<li>api\_gateway</li>

<li>orchestrator</li>

<li>nextflow\_worker</li>

<li>model\_service</li>

<li>inference\_engine</li>

<li>llm\_service</li>

<li>frontend</li>

</ul>



Per controllare eventuali errori nei log:



<div class="code">

docker compose logs -f

</div>



Oppure per un singolo servizio:



<div class="code">

docker compose logs -f orchestrator

</div>





<h2>Test pipeline Nextflow</h2>



La pipeline neuroimaging può essere verificata caricando una MRI cerebrale in formato NIfTI tramite la dashboard clinica.



Procedura:



<ul>

<li>accedere alla dashboard clinica</li>

<li>caricare un file MRI (.nii oppure .nii.gz)</li>

<li>avviare l’elaborazione</li>

<li>monitorare lo stato del task</li>

</ul>



Durante l’esecuzione devono essere completate le seguenti fasi:



<div class="code">

MRI → FreeSurfer → ROI extraction → Radiomics → CSV generation

</div>



Lo stato del workflow può essere monitorato nei log:



<div class="code">

docker compose logs -f nextflow\_worker

</div>



Il completamento della pipeline produce un dataset radiomico in formato CSV utilizzato dal classificatore.





<h2>Test classificatore</h2>



Il servizio <strong>model\_service</strong> recupera automaticamente il modello champion registrato su MLflow tramite DagsHub.



Per verificare il corretto funzionamento del classificatore:



<ul>

<li>eseguire una pipeline completa</li>

<li>attendere la fase di inferenza</li>

<li>verificare la restituzione della predizione</li>

</ul>



Output atteso:



<ul>

<li>classe diagnostica (bvFTD oppure HC)</li>

<li>probabilità associata alla classificazione</li>

<li>coordinate nello spazio latente UMAP</li>

</ul>



Eventuali errori possono essere verificati tramite:



<div class="code">

docker compose logs -f model\_service

</div>



oppure:



<div class="code">

docker compose logs -f inference\_engine

</div>





<h2>Test dashboard</h2>



Il frontend React consente la visualizzazione interattiva dei risultati clinici.



Verificare:



<ul>

<li>upload corretto file MRI (.nii / .nii.gz)</li>

<li>visualizzazione multiplanare tramite viewer NiiVue</li>

<li>visualizzazione embedding tridimensionale UMAP</li>

<li>posizione del paziente nello spazio latente</li>

<li>confronto con dataset di riferimento</li>

<li>funzionamento assistente AI clinico</li>

</ul>



Testare l’assistente LLM verificando:



<ul>

<li>risposta a query contestuali</li>

<li>interpretazione della predizione diagnostica</li>

<li>supporto alla navigazione dello spazio latente</li>

</ul>





<h2>Verifica completa sistema</h2>



Il sistema è considerato correttamente funzionante quando:



<ul>

<li>tutti i container risultano attivi</li>

<li>la pipeline Nextflow termina senza errori</li>

<li>viene generato il dataset radiomico</li>

<li>il classificatore restituisce una predizione</li>

<li>la dashboard visualizza correttamente MRI e UMAP</li>

</ul>



In queste condizioni la piattaforma ClinicalTwin è pronta per l’utilizzo in ambiente di ricerca clinica sperimentale.

