<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Quickstart</title>

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

<h1>Quickstart – Avvio rapido della piattaforma MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
Questa guida descrive i passaggi essenziali per eseguire la prima analisi MRI
utilizzando la piattaforma MLOps.
</p>

<p>
Il flusso comprende l’avvio dei microservizi, la configurazione iniziale
e l’esecuzione completa della pipeline radiomica fino alla visualizzazione
dei risultati diagnostici.
</p>

</div>

<div class="section">
<h2>2. Avvio dello stack</h2>

<p>
Dopo aver completato installazione e configurazione, avviare
l’intero sistema tramite Docker Compose:
</p>

<pre>
docker compose up -d --build
</pre>

<p>
Attendere che tutti i container risultino attivi.
</p>

</div>

<div class="section">
<h2>3. Accesso alla piattaforma</h2>

<p>
Una volta avviato lo stack, la dashboard è disponibile al seguente indirizzo:
</p>

<pre>
http://localhost:5173
</pre>

<p>
Le API sono accessibili tramite Swagger UI:
</p>

<pre>
http://localhost:8000/docs
</pre>

</div>

<div class="section">
<h2>4. Creazione del primo utente</h2>

<p>
Al primo avvio è necessario registrare un utente tramite API Gateway.
</p>

<pre>
POST /signup
</pre>

<p>
Dopo la registrazione è possibile effettuare il login e accedere
alle funzionalità della piattaforma.
</p>

</div>

<div class="section">
<h2>5. Upload della MRI</h2>

<p>
Dopo il login, è possibile caricare una risonanza magnetica
in formato:
</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>
Il file viene salvato nel volume condiviso e registrato
come task asincrono.
</p>

</div>

<div class="section">
<h2>6. Esecuzione della pipeline</h2>

<p>
Dopo l’upload, la pipeline viene avviata automaticamente
dal servizio orchestrator.
</p>

<p>Fasi principali:</p>

<ul>
<li>segmentazione anatomica</li>
<li>estrazione ROI</li>
<li>estrazione feature radiomiche</li>
<li>inferenza diagnostica</li>
<li>proiezione UMAP</li>
</ul>

<p>
Lo stato della pipeline può essere monitorato tramite dashboard.
</p>

</div>

<div class="section">
<h2>7. Visualizzazione risultati</h2>

<p>
Al termine dell’elaborazione, i risultati sono disponibili nella dashboard.
</p>

<ul>
<li>segmentazione MRI (viewer multiplanare)</li>
<li>classe diagnostica</li>
<li>confidence score</li>
<li>posizione nello spazio UMAP</li>
<li>nearest neighbors</li>
</ul>

</div>

<div class="section">
<h2>8. Interazione con assistente AI</h2>

<p>
L’assistente AI consente di ottenere spiegazioni cliniche
sui risultati ottenuti.
</p>

<p>
È possibile:
</p>

<ul>
<li>interpretare le feature radiomiche</li>
<li>analizzare la posizione nel cluster diagnostico</li>
<li>richiedere spiegazioni contestualizzate</li>
</ul>

</div>

<div class="section">
<h2>9. Flusso completo</h2>

<pre>
Login
   ↓
Upload MRI
   ↓
Pipeline radiomica
   ↓
Inferenza KNN
   ↓
Embedding UMAP
   ↓
Visualizzazione dashboard
   ↓
Explainability AI
</pre>

<p>
Questo flusso rappresenta il ciclo completo di analisi
supportato dalla piattaforma.
</p>

</div>

<div class="section">
<h2>10. Conclusioni</h2>

<p>
Il Quickstart consente di eseguire rapidamente una pipeline
radiomica completa senza configurazioni avanzate.
</p>

<p>
Per utilizzi più avanzati (scalabilità, GPU, configurazioni
multi-ambiente), fare riferimento alle sezioni dedicate
di Deployment e Configuration.
</p>

</div>

</div>

</body>

</html>
