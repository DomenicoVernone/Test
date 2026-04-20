<style>

.testbox {

&#x20; border-left: 6px solid #4caf50;

&#x20; background: #edf7ed;

&#x20; padding: 14px;

&#x20; margin: 16px 0;

&#x20; border-radius: 6px;

}

</style>



<h1>Testing</h1>



<div class="testbox">

Questa sezione descrive le procedure di verifica funzionale della piattaforma ClinicalTwin.

</div>



<h2>Test container Docker</h2>



<pre>

docker compose ps

</pre>



Verificare stato:



<ul>

<li>api\_gateway</li>

<li>orchestrator</li>

<li>nextflow\_worker</li>

<li>model\_service</li>

<li>inference\_engine</li>

<li>llm\_service</li>

<li>frontend</li>

</ul>



<h2>Test pipeline Nextflow</h2>



Procedura:



<ul>

<li>caricare MRI</li>

<li>avviare pipeline</li>

<li>monitorare task</li>

</ul>



<h2>Test classificatore</h2>



Output atteso:



<ul>

<li>classe diagnostica</li>

<li>probabilità</li>

<li>embedding UMAP</li>

</ul>



<h2>Test dashboard</h2>



Verificare:



<ul>

<li>viewer multiplanare</li>

<li>visualizzazione UMAP</li>

<li>assistente AI</li>

</ul>



<h2>Verifica completa sistema</h2>



Sistema operativo se:



<ul>

<li>pipeline completata</li>

<li>dataset generato</li>

<li>predizione disponibile</li>

<li>UMAP visualizzato</li>

</ul>

