<style>
.arch-container {
  border-left: 6px solid #009688;
  background: #eefaf8;
  padding: 18px;
  border-radius: 6px;
  margin: 20px 0;
}

.diagram-box {
  font-family: monospace;
  background: #f4f6fa;
  padding: 20px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre;
  line-height: 1.4;
}
</style>


<h1>Architettura</h1>


<div class="arch-container">

<p>
ClinicalTwin è progettato secondo un’architettura a microservizi containerizzati orchestrati tramite Docker Compose, con l’obiettivo di garantire modularità, riproducibilità computazionale e separazione delle responsabilità tra i diversi componenti della pipeline di analisi neuroimaging.
</p>

<p>
Il sistema integra servizi dedicati alla gestione dell’autenticazione, orchestrazione delle elaborazioni, preprocessing MRI automatizzato, inferenza statistica, gestione dei modelli di classificazione e visualizzazione interattiva dei risultati clinici. Questa organizzazione consente l’esecuzione asincrona delle pipeline radiomiche e facilita l’estensione futura della piattaforma con nuovi moduli diagnostici.
</p>

<p>
Ogni servizio opera in modo indipendente all’interno di un container Docker, comunicando tramite API REST interne alla rete applicativa.
</p>

</div>


<h2>Diagramma architetturale</h2>


<div class="diagram-box">

+----------------------+
|       Frontend       |
|     React + NiiVue   |
+----------+-----------+
           |
           |
+----------v-----------+
|      API Gateway     |
|    FastAPI + JWT     |
+----------+-----------+
           |
+----------+------------------+
|                             |
|                             |
v                             v
+-----------+-----------+     +-----------------------+
|      Orchestrator     |     |      LLM Service      |
|   Task coordination   |     | Spatial RAG Assistant |
+-----------+-----------+     +-----------------------+
            |
            |
+-----------v-----------+
|     Nextflow Worker   |
|  FreeSurfer / Radiomics
+-----------+-----------+
            |
            |
+-----------v-----------+
|     Model Service     |
|    MLflow + DagsHub   |
+-----------+-----------+
            |
            |
+-----------v-----------+
|   Inference Engine    |
|     R + UMAP + KNN    |
+-----------------------+

</div>