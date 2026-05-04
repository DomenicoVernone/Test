<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Test Plan</title>

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

<h1>🧪 Test Plan – Validazione del sistema MLOps</h1>

<div class="section">
<h2>1. Introduzione</h2>

<p>
Questo documento descrive la strategia di testing adottata per garantire
la correttezza, la robustezza e l’affidabilità della piattaforma MLOps.
</p>

<p>
A differenza di sistemi monolitici, l’architettura a microservizi richiede
una validazione su più livelli: singoli componenti, comunicazione tra servizi
e comportamento complessivo del sistema.
</p>

<p>
Il testing è quindi progettato per coprire l’intero ciclo di vita dell’analisi,
dall’input MRI fino alla generazione della diagnosi e della sua interpretazione.
</p>

</div>

<div class="section">
<h2>2. Obiettivi del testing</h2>

<p>
L’obiettivo principale è garantire che ogni componente del sistema operi
correttamente sia in isolamento che in integrazione con gli altri servizi.
</p>

<ul>
<li>verificare il corretto funzionamento dei microservizi</li>
<li>validare il flusso end-to-end</li>
<li>identificare errori e condizioni limite</li>
<li>garantire stabilità sotto carico</li>
<li>assicurare consistenza dei dati tra pipeline e inferenza</li>
</ul>

</div>

<div class="section">
<h2>3. Livelli di test</h2>

<p>
Il testing è organizzato su più livelli per intercettare errori
nelle diverse fasi del sistema.
</p>

<table>

<tr>
<th>Livello</th>
<th>Descrizione</th>
</tr>

<tr>
<td>Unit Test</td>
<td>Verifica del comportamento di singole funzioni o moduli isolati</td>
</tr>

<tr>
<td>Integration Test</td>
<td>Validazione della comunicazione tra microservizi</td>
</tr>

<tr>
<td>System Test</td>
<td>Verifica del sistema completo in ambiente controllato</td>
</tr>

<tr>
<td>End-to-End Test</td>
<td>Simulazione completa del flusso utente reale</td>
</tr>

</table>

<p>
Questa stratificazione consente di individuare rapidamente l’origine
degli errori e ridurre i tempi di debugging.
</p>

</div>

<div class="section">
<h2>4. Test funzionali</h2>

<p>
I test funzionali verificano che ogni componente produca l’output atteso
a fronte di un input valido.
</p>

<table>

<tr>
<th>Test</th>
<th>Descrizione</th>
<th>Risultato atteso</th>
</tr>

<tr>
<td>Login utente</td>
<td>Autenticazione tramite API Gateway</td>
<td>Token JWT valido</td>
</tr>

<tr>
<td>Upload MRI</td>
<td>Caricamento file MRI nel sistema</td>
<td>File salvato correttamente</td>
</tr>

<tr>
<td>Avvio pipeline</td>
<td>Creazione task orchestrator</td>
<td>Task in stato pending/running</td>
</tr>

<tr>
<td>Inferenza</td>
<td>Esecuzione classificazione KNN</td>
<td>Classe diagnostica restituita</td>
</tr>

<tr>
<td>LLM</td>
<td>Generazione spiegazione clinica</td>
<td>Output testuale coerente</td>
</tr>

</table>

<p>
Questi test garantiscono che le funzionalità principali del sistema
siano operative e coerenti con le specifiche.
</p>

</div>

<div class="section">
<h2>5. Test end-to-end</h2>

<p>
I test end-to-end rappresentano il livello più critico, in quanto
verificano il comportamento del sistema nella sua interezza.
</p>

<pre>
Login
   ↓
Upload MRI
   ↓
Pipeline Nextflow
   ↓
Feature Extraction
   ↓
Inferenza
   ↓
UMAP
   ↓
Explainability
</pre>

<p>
Durante questi test viene verificata:
</p>

<ul>
<li>la corretta sequenza di esecuzione</li>
<li>la consistenza dei dati tra i servizi</li>
<li>l’assenza di errori intermedi</li>
</ul>

<p>
Questo livello di testing è fondamentale per identificare problemi
di integrazione difficilmente rilevabili nei test unitari.
</p>

</div>

<div class="section">
<h2>6. Test di performance</h2>

<p>
I test di performance valutano la capacità del sistema di gestire
carichi computazionali elevati.
</p>

<table>

<tr>
<th>Test</th>
<th>Descrizione</th>
<th>Obiettivo</th>
</tr>

<tr>
<td>Tempo pipeline</td>
<td>Durata complessiva analisi MRI</td>
<td>Tempo accettabile</td>
</tr>

<tr>
<td>Parallelizzazione</td>
<td>Esecuzione simultanea di più analisi</td>
<td>Nessun degrado significativo</td>
</tr>

<tr>
<td>GPU test</td>
<td>Utilizzo FastSurfer CUDA</td>
<td>Riduzione tempi</td>
</tr>

</table>

<p>
Questi test sono essenziali per valutare la scalabilità del sistema
in scenari reali.
</p>

</div>

<div class="section">
<h2>7. Test di resilienza</h2>

<p>
I test di resilienza verificano la capacità del sistema di gestire
errori e condizioni anomale.
</p>

<table>

<tr>
<th>Scenario</th>
<th>Comportamento atteso</th>
</tr>

<tr>
<td>Errore pipeline</td>
<td>Interruzione immediata (fail-fast)</td>
</tr>

<tr>
<td>Servizio non disponibile</td>
<td>Errore propagato correttamente</td>
</tr>

<tr>
<td>Input non valido</td>
<td>Gestione controllata dell’errore</td>
</tr>

</table>

<p>
Questo approccio garantisce che il sistema non produca output inconsistenti.
</p>

</div>

<div class="section">
<h2>8. Test di sicurezza</h2>

<p>
I test di sicurezza verificano la protezione degli endpoint e
la gestione delle credenziali.
</p>

<ul>
<li>validazione token JWT</li>
<li>accesso autenticato agli endpoint</li>
<li>protezione dati sensibili</li>
</ul>

</div>

<div class="section">
<h2>9. Test API</h2>

<p>
Le API vengono testate tramite Swagger UI e richieste HTTP manuali.
</p>

<pre>
http://localhost:8000/docs
</pre>

<p>
Vengono verificati:
</p>

<ul>
<li>correttezza delle risposte JSON</li>
<li>codici HTTP appropriati</li>
<li>validazione input/output</li>
</ul>

</div>

<div class="section">
<h2>10. Automazione dei test</h2>

<p>
Per garantire continuità nel testing, è possibile integrare strumenti
di automazione:
</p>

<ul>
<li>pytest per backend</li>
<li>test API automatici</li>
<li>pipeline CI/CD</li>
</ul>

<p>
L’automazione consente di rilevare regressioni in modo tempestivo.
</p>

</div>

<div class="section">
<h2>11. Metriche di validazione</h2>

<p>
Le metriche consentono di valutare oggettivamente le prestazioni del sistema.
</p>

<table>

<tr>
<th>Metrica</th>
<th>Descrizione</th>
</tr>

<tr>
<td>Accuracy</td>
<td>Accuratezza del modello diagnostico</td>
</tr>

<tr>
<td>Latency</td>
<td>Tempo di risposta del sistema</td>
</tr>

<tr>
<td>Error rate</td>
<td>Percentuale di errori durante l’esecuzione</td>
</tr>

</table>

</div>

<div class="section">
<h2>12. Conclusioni</h2>

<p>
Il test plan adottato garantisce una validazione completa e sistematica
della piattaforma MLOps.
</p>

<p>
L’approccio multilivello consente di individuare rapidamente problemi,
garantendo affidabilità e stabilità del sistema nel tempo.
</p>

</div>

</div>

</body>

</html>
