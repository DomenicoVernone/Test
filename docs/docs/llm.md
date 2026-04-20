<style>

.llm-box {

&#x20; border-left: 6px solid #9c27b0;

&#x20; background: #f5ecfa;

&#x20; padding: 18px;

&#x20; border-radius: 6px;

}

</style>



<h1>Assistente LLM Clinico</h1>



<div class="llm-box">

ClinicalTwin integra un assistente AI basato su Spatial Retrieval-Augmented Generation (Spatial RAG).

</div>



<h2>Funzioni principali</h2>



<ul>

<li>interpretazione predizione diagnostica</li>

<li>spiegazione embedding UMAP</li>

<li>analisi feature radiomiche</li>

<li>supporto conversazionale multi-turno</li>

</ul>



<h2>Architettura</h2>



Servizio:



<code>llm\_service</code>



Tecnologia:



<ul>

<li>FastAPI</li>

<li>Groq API</li>

<li>JWT authentication</li>

</ul>



<h2>Endpoint principale</h2>



POST /chat



Input:



<pre>

{

&#x20;"message": "Interpret the diagnostic result"

}

</pre>



Output:



<pre>

{

&#x20;"response": "The radiomic profile suggests compatibility with bvFTD."

}

</pre>

