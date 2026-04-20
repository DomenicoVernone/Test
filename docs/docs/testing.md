<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">
<title>Clinical Twin – Testing</title>

<style>

/* ===== GLOBAL ===== */

body {
    margin: 0;
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    background: #f5f6f7;
}

/* ===== CONTENT ===== */

.content {
    margin-left: 0px;
    padding: 40px;
    max-width: 900px;
}

/* ===== BREADCRUMB ===== */

.breadcrumb {
    color: #6c6c6c;
    font-size: 14px;
    margin-bottom: 10px;
}

/* ===== HEADINGS ===== */

h1 {
    font-size: 36px;
    margin-bottom: 25px;
}

h2 {
    margin-top: 40px;
    font-size: 26px;
}

/* ===== SERVICE BOX ===== */

.service-box {
    background: white;
    padding: 18px;
    border-radius: 8px;
    margin-top: 20px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}

/* ===== CODE BLOCK ===== */

.codeblock {
    background: #eeeeee;
    padding: 14px;
    border-radius: 6px;
    font-family: monospace;
    margin: 15px 0;
    white-space: pre-line;
}

/* ===== NAV BUTTONS ===== */

.nav-buttons {
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
}

.button {
    background: #e0e0e0;
    border-radius: 6px;
    padding: 10px 15px;
    text-decoration: none;
    color: black;
}

/* ===== FOOTER ===== */

.footer {
    margin-top: 50px;
    font-size: 14px;
    color: gray;
}

</style>

</head>


<body>

<div class="content">

<div class="breadcrumb">
Docs » Testing
</div>

<h1>Testing</h1>


<div class="service-box">

<p>
Clinical Twin include una serie di test funzionali e di integrazione per
verificare il corretto funzionamento dei microservizi, della pipeline
neuroimaging e del motore di inferenza diagnostica.
</p>

</div>


<h2>Verifica stato microservizi</h2>

<div class="service-box">

<p>
Dopo l’avvio dello stack Docker è possibile controllare la disponibilità
dei servizi tramite endpoint di health-check.
</p>

<div class="codeblock">
curl http://localhost:8000/docs
curl http://localhost:8001/docs
curl http://localhost:8002/docs
curl http://localhost:8003/docs
curl http://localhost:8004
</div>

</div>


<h2>Test autenticazione</h2>

<div class="service-box">

<p>
Verificare la creazione di un nuovo utente tramite Swagger UI:
</p>

<div class="codeblock">
POST /signup
</div>

<p>
Successivamente eseguire il login:
</p>

<div class="codeblock">
POST /login
</div>

<p>
Se l’autenticazione ha successo viene restituito un token JWT valido.
</p>

</div>


<h2>Test pipeline neuroimaging</h2>

<div class="service-box">

<p>
Caricare una MRI T1-weighted tramite dashboard e verificare:
</p>

<ul>
<li>avvio task asincrono</li>
<li>segmentazione FreeSurfer / FastSurfer</li>
<li>estrazione ROI</li>
<li>estrazione feature radiomiche</li>
</ul>

</div>


<h2>Test estrazione radiomica</h2>

<div class="service-box">

<p>
Durante l’esecuzione della pipeline devono essere generati i seguenti output:
</p>

<div class="codeblock">
ROI_labels.tsv loaded
Radiomics features extracted
pyradiomics.yaml applied
</div>

</div>


<h2>Test inferenza diagnostica</h2>

<div class="service-box">

<p>
Il servizio inference_engine restituisce una predizione diagnostica
basata su classificazione KNN.
</p>

<p>Esempio output:</p>

<div class="codeblock">
{
  "prediction": "bvFTD",
  "confidence": 0.81,
  "neighbors": [...]
}
</div>

</div>


<h2>Test proiezione UMAP</h2>

<div class="service-box">

<p>
Verificare la corretta generazione delle coordinate nello spazio latente:
</p>

<div class="codeblock">
UMAP projection computed
3D embedding available
</div>

</div>


<h2>Test dashboard clinica</h2>

<div class="service-box">

<p>
Dalla dashboard React verificare:
</p>

<ul>
<li>visualizzazione multiplanare MRI (NiiVue)</li>
<li>posizione nello spazio UMAP</li>
<li>classe diagnostica stimata</li>
<li>storico task eseguiti</li>
</ul>

</div>


<h2>Test assistente AI</h2>

<div class="service-box">

<p>
Verificare la connessione al servizio LLM tramite richiesta testuale:
</p>

<div class="codeblock">
Explain why this patient is close to svPPA cluster
</div>

<p>
L’assistente deve restituire una risposta coerente con il contesto
radiomico e la posizione nello spazio latente.
</p>

</div>


<h2>Test end-to-end</h2>

<div class="service-box">

<p>
Scenario completo di validazione:
</p>

<div class="codeblock">
Upload MRI → Segmentazione → Radiomics → Inferenza → UMAP → Dashboard → Explainability AI
</div>

<p>
Se tutte le fasi vengono completate senza errori, la pipeline Clinical Twin
è correttamente configurata.
</p>

</div>



</div>

</body>
</html>