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

<div class="content">

<div class="breadcrumb">
Docs » Introduzione
</div>

<h1>Introduzione</h1>

<h2>Panoramica del sistema</h2>

<div class="service-box">

<p>
MLOps è una piattaforma avanzata di supporto alle decisioni cliniche progettata
per la diagnosi differenziale delle varianti di Demenza Frontotemporale (FTD)
attraverso l’analisi automatizzata di immagini di risonanza magnetica (MRI)
strutturale.
</p>

<p>
Il sistema integra una pipeline completa di processamento neuroimaging,
estrazione radiomica, inferenza statistica e interpretazione assistita
tramite modelli AI, seguendo i principi dell’ingegneria MLOps:
riproducibilità, scalabilità e modularità.
</p>

<p>
L’obiettivo è trasformare dati di imaging complessi in informazioni cliniche
strutturate e interpretabili, riducendo la variabilità operatore-dipendente
e supportando il processo decisionale medico.
</p>

</div>

<h2>Architettura logica</h2>

<div class="service-box">

<p>
La piattaforma è costruita secondo un’architettura a microservizi containerizzati,
in cui ogni componente implementa una responsabilità ben definita all’interno
del workflow diagnostico.
</p>

<p>
I principali moduli del sistema includono:
</p>

<ul>
<li><b>Pipeline neuroimaging</b> (Nextflow) per preprocessing MRI e radiomica</li>
<li><b>Orchestrator</b> per la gestione dei task asincroni</li>
<li><b>Model service</b> per accesso e versioning dei modelli ML</li>
<li><b>Inference engine</b> per classificazione diagnostica e embedding UMAP</li>
<li><b>LLM service</b> per interpretazione clinica (Spatial RAG)</li>
<li><b>Frontend React</b> per visualizzazione e interazione clinica</li>
</ul>

<p>
Questa separazione consente un’elevata scalabilità del sistema e facilita
l’integrazione di nuovi modelli o componenti senza impattare il resto
dell’architettura.
</p>

</div>

<h2>Flusso operativo end-to-end</h2>

<div class="service-box">

<p>
Il sistema implementa un workflow completamente automatizzato che parte
dal caricamento della MRI e termina con la produzione di una diagnosi
assistita e interpretabile.
</p>

<div class="codeblock">
1. Upload MRI (frontend)
2. Autenticazione e routing (api_gateway)
3. Creazione task analisi (orchestrator)
4. Esecuzione pipeline radiomica (nextflow_worker)
5. Generazione feature radiomiche (CSV)
6. Caricamento modello ML (model_service)
7. Inferenza diagnostica (inference_engine)
8. Proiezione nello spazio latente UMAP
9. Interpretazione AI (llm_service)
10. Visualizzazione risultati (frontend)
</div>

<p>
Questo flusso garantisce coerenza tra i diversi componenti e consente
l’esecuzione riproducibile delle analisi su dataset clinici.
</p>

</div>

<h2>Pipeline neuroimaging e radiomica</h2>

<div class="service-box">

<p>
La pipeline implementa una sequenza deterministica di operazioni per
l’elaborazione delle immagini MRI strutturali:
</p>

<ul>
<li>segmentazione anatomica (FreeSurfer / FastSurfer)</li>
<li>estrazione delle regioni di interesse (ROI)</li>
<li>calcolo delle feature radiomiche (PyRadiomics)</li>
</ul>

<p>
Il risultato è un vettore di feature quantitative che rappresenta
le caratteristiche morfologiche e testurali delle strutture cerebrali.
</p>

<p>
Queste feature costituiscono l’input per il modello di inferenza
diagnostica.
</p>

</div>

<h2>Inferenza e interpretabilità</h2>

<div class="service-box">

<p>
Il sistema utilizza un approccio di inferenza basato su:
</p>

<ul>
<li>classificazione K-Nearest Neighbors (KNN)</li>
<li>proiezione nello spazio latente tridimensionale (UMAP)</li>
</ul>

<p>
Questo consente non solo di ottenere una predizione diagnostica,
ma anche di posizionare il paziente in uno spazio interpretabile
basato sulla similarità clinica.
</p>

<p>
L’assistente AI (LLM service) arricchisce il processo fornendo
spiegazioni contestualizzate basate su:
</p>

<ul>
<li>feature radiomiche</li>
<li>posizione nello spazio UMAP</li>
<li>cluster diagnostici</li>
</ul>

<p>
Questo approccio migliora significativamente l’explainability del sistema,
rendendo le predizioni più comprensibili per l’utente clinico.
</p>

</div>

<h2>Caratteristiche principali</h2>

<div class="service-box">

<ul>
<li>Pipeline MRI completamente automatizzata</li>
<li>Architettura a microservizi containerizzata</li>
<li>Riproducibilità garantita tramite Nextflow</li>
<li>Integrazione con MLflow e Model Registry</li>
<li>Inferenza interpretabile (KNN + UMAP)</li>
<li>Explainability tramite LLM (Spatial RAG)</li>
<li>Dashboard clinica interattiva in React</li>
</ul>

</div>

<h2>Contesto applicativo</h2>

<div class="service-box">

<p>
La piattaforma è sviluppata come progetto accademico nell’ambito della
ricerca su sistemi di supporto decisionale clinico e applicazioni di
machine learning al neuroimaging.
</p>

<p>
Il sistema è progettato per essere utilizzato in:
</p>

<ul>
<li>contesti di ricerca neuroimaging</li>
<li>ambienti accademici</li>
<li>workflow sperimentali di diagnosi assistita</li>
</ul>

<p>
Non è destinato all’uso clinico diretto senza validazione regolatoria.
</p>

</div>

</div>

</body>

</html>
