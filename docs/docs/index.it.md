<!DOCTYPE html>

<html lang="it">

<head>
<meta charset="UTF-8">
<title>MLOps – Introduzione</title>

<style>
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 40px;
    background-color: #f9f9f9;
    color: #333;
}

h1, h2, h3 {
    color: #2c3e50;
}

h1 {
    border-bottom: 2px solid #ccc;
    padding-bottom: 10px;
}

pre {
    background-color: #eee;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

.section {
    margin-bottom: 40px;
}

.box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

ul {
    margin-left: 20px;
}

/* ===== TABLE STYLE UNIFICATO ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
    font-size: 14px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
}

th {
    background-color: #2c3e50;
    color: white;
    text-align: left;
    padding: 12px;
    font-weight: 600;
}

td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

tr:hover {
    background-color: #eef2f5;
}
</style>

</head>

<body>

<div class="box">

<h1>Introduzione</h1>

<div class="section">
<h2>1. Panoramica del sistema</h2>

<p>
MLOps è una piattaforma avanzata di supporto alle decisioni cliniche progettata
per la diagnosi differenziale delle varianti di Demenza Frontotemporale (FTD)
attraverso l’analisi automatizzata di immagini di risonanza magnetica (MRI).
</p>

<p>
Il sistema integra una pipeline completa di processamento neuroimaging,
estrazione radiomica, inferenza statistica e interpretazione assistita
tramite modelli AI, seguendo i principi MLOps di riproducibilità,
scalabilità e modularità.
</p>

<p>
L’obiettivo è trasformare dati complessi in informazioni cliniche
interpretabili, supportando il processo decisionale medico.
</p>

</div>

<div class="section">
<h2>2. Architettura logica</h2>

<p>
La piattaforma è costruita secondo un’architettura a microservizi
containerizzati, in cui ogni componente implementa una responsabilità
specifica nel workflow diagnostico.
</p>

<ul>
<li><b>Pipeline neuroimaging</b> (Nextflow)</li>
<li><b>Orchestrator</b> (gestione task)</li>
<li><b>Model Service</b> (MLflow)</li>
<li><b>Inference Engine</b> (KNN + UMAP)</li>
<li><b>LLM Service</b> (Explainability)</li>
<li><b>Frontend React</b></li>
</ul>

<p>
Questa separazione consente scalabilità e facilità di estensione.
</p>

</div>

<div class="section">
<h2>3. Flusso operativo end-to-end</h2>

<p>
Il sistema implementa un workflow automatizzato dalla MRI alla diagnosi.
</p>

<pre>
1. Upload MRI
2. API Gateway (JWT)
3. Orchestrator
4. Pipeline Nextflow
5. Radiomics Features (CSV)
6. Model Service
7. Inference Engine
8. UMAP Projection
9. LLM Explainability
10. Visualizzazione
</pre>

<p>
Il flusso garantisce coerenza e riproducibilità delle analisi.
</p>

</div>

<div class="section">
<h2>4. Pipeline neuroimaging e radiomica</h2>

<p>
La pipeline esegue una sequenza deterministica:
</p>

<ul>
<li>segmentazione (FreeSurfer / FastSurfer)</li>
<li>estrazione ROI</li>
<li>feature radiomiche (PyRadiomics)</li>
</ul>

<p>
L’output è un vettore di feature utilizzato per l’inferenza.
</p>

</div>

<div class="section">
<h2>5. Inferenza e interpretabilità</h2>

<p>
Il sistema utilizza:
</p>

<ul>
<li>KNN per classificazione</li>
<li>UMAP per embedding 3D</li>
</ul>

<p>
L’LLM fornisce interpretazioni basate su feature e contesto.
</p>

</div>

<div class="section">
<h2>6. Caratteristiche principali</h2>

<ul>
<li>Pipeline MRI automatizzata</li>
<li>Architettura a microservizi</li>
<li>Riproducibilità con Nextflow</li>
<li>Integrazione MLflow</li>
<li>Explainability AI</li>
</ul>

</div>

<div class="section">
<h2>7. Contesto applicativo</h2>

<p>
La piattaforma è sviluppata in ambito accademico per ricerca
nel campo del neuroimaging e dei sistemi di supporto decisionale.
</p>

<p>
Non è destinata all’uso clinico diretto senza validazione regolatoria.
</p>

</div>

</div>

</body>

</html>
