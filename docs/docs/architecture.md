<style>
.arch-box {
  border-left: 6px solid #009688;
  background: #eefaf8;
  padding: 18px;
  border-radius: 6px;
  margin: 20px 0;
}
.diagram {
  font-family: monospace;
  background: #f4f6fa;
  padding: 20px;
  border-radius: 6px;
}
</style>

<h1>Architettura del sistema</h1>

<div class="arch-box">
ClinicalTwin adotta un’architettura a microservizi containerizzati orchestrati tramite Docker Compose, garantendo modularità, scalabilità e riproducibilità computazionale.
</div>

<h2>Componenti principali</h2>

<ul>
<li>Frontend React</li>
<li>API Gateway (FastAPI + JWT)</li>
<li>Orchestrator</li>
<li>Nextflow Worker</li>
<li>Model Service</li>
<li>Inference Engine (R)</li>
<li>LLM Service</li>
</ul>

<h2>Diagramma architetturale</h2>

<div class="diagram">

Frontend  
↓  
API Gateway  
↓  
Orchestrator  
↓  
Nextflow Worker  
↓  
Model Service  
↓  
Inference Engine  

Parallelamente:

LLM Service
</div>