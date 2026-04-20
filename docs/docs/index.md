<style>

:root {
  --primary: #3f51b5;
  --secondary: #009688;
  --background-primary: #eef2ff;
  --background-secondary: #eefaf8;
  --text-main: #1f2937;
  --text-soft: #4b5563;
}

body {
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  line-height: 1.65;
  color: var(--text-main);
  max-width: 1100px;
  margin: auto;
  padding: 30px;
}

h1 {
  font-size: 2.2rem;
  margin-bottom: 20px;
}

h2 {
  margin-top: 10px;
  margin-bottom: 12px;
}

.hero {
  border-left: 6px solid var(--primary);
  background: var(--background-primary);
  padding: 22px;
  border-radius: 8px;
  margin: 28px 0;
}

.section {
  border-left: 6px solid var(--secondary);
  background: var(--background-secondary);
  padding: 22px;
  border-radius: 8px;
  margin: 32px 0;
}

.section-title {
  font-weight: 600;
  margin-bottom: 10px;
}

ul {
  margin-top: 8px;
  margin-bottom: 8px;
}

li {
  margin-bottom: 6px;
}

.highlight {
  font-weight: 600;
  color: var(--secondary);
}

.note {
  margin-top: 12px;
  color: var(--text-soft);
}

</style>

<h1>
ClinicalTwin – Sistema per l’analisi automatizzata di immagini MRI nella diagnosi differenziale della bvFTD
</h1>

<div class="hero">

<p>
<strong>ClinicalTwin</strong> è una piattaforma software modulare progettata per supportare l’analisi automatizzata di immagini di risonanza magnetica cerebrale strutturale (<span class="highlight">MRI T1-pesata</span>) nel contesto della diagnosi differenziale delle patologie neurodegenerative frontotemporali.
</p>

<p>
Il sistema implementa una pipeline completa di elaborazione neuroimaging che integra:
</p>

<ul>
<li>segmentazione anatomica cerebrale automatizzata</li>
<li>estrazione di feature radiomiche regionali</li>
<li>costruzione di vettori quantitativi ad alta dimensionalità</li>
<li>classificazione supervisionata tramite modelli di machine learning</li>
</ul>

<p>
L’architettura è basata su microservizi containerizzati orchestrati tramite <strong>Docker</strong> e workflow computazionali gestiti mediante <strong>Nextflow</strong>, garantendo elevati livelli di riproducibilità, scalabilità e portabilità dell’intero processo di analisi.
</p>

<p>
ClinicalTwin consente l’automazione completa del flusso di elaborazione, dalla ricezione dell’immagine MRI fino alla generazione della predizione diagnostica.
</p>

</div>

<div class="section">

<h2 class="section-title">Cos’è ClinicalTwin</h2>

<p>
ClinicalTwin è una piattaforma software modulare per l’analisi automatizzata di immagini MRI cerebrali strutturali finalizzata alla diagnosi differenziale della
<strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong>.
</p>

<p>Il sistema integra:</p>

<ul>
<li>segmentazione anatomica cerebrale automatizzata</li>
<li>estrazione di biomarcatori radiomici regionali</li>
<li>costruzione di vettori di feature quantitative ad alta dimensionalità</li>
<li>classificazione supervisionata tramite modelli di machine learning</li>
<li>strumenti di visualizzazione interattiva per l’interpretazione clinica dei risultati</li>
</ul>

</div>

<div class="section">

<h2 class="section-title">Obiettivo clinico</h2>

<p>
L’obiettivo principale della piattaforma è supportare il processo di diagnosi differenziale tra:
</p>

<ul>
<li><strong>Healthy Controls (HC)</strong></li>
<li><strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong></li>
</ul>

<p>
mediante l’analisi quantitativa di immagini MRI strutturali ad alta risoluzione.
</p>

<p class="note">
Questo approccio consente di integrare biomarcatori morfometrici oggettivi nel processo diagnostico, contribuendo alla valutazione precoce delle patologie neurodegenerative frontotemporali.
</p>

</div>

<div class="section">

<h2 class="section-title">Formato dei dati di input MRI</h2>

<p>
ClinicalTwin utilizza immagini MRI strutturali T1-pesate nei seguenti formati standard:
</p>

<ul>
<li>.nii</li>
<li>.nii.gz</li>
</ul>

<p>Le immagini devono essere:</p>

<ul>
<li>volumetriche tridimensionali (3D)</li>
<li>acquisite con sequenze T1-weighted ad alta risoluzione</li>
<li>compatibili con la pipeline di segmentazione FreeSurfer</li>
<li>preferibilmente organizzate secondo lo standard BIDS</li>
</ul>

<p class="note">
Durante il preprocessing, le immagini vengono trasformate automaticamente in vettori strutturati di biomarcatori quantitativi utilizzabili per l’inferenza computazionale.
</p>

</div>

<div class="section">

<h2 class="section-title">Output della pipeline diagnostica</h2>

<p>
Al termine della pipeline di elaborazione, ClinicalTwin restituisce:
</p>

<ul>
<li>classe predetta (<strong>Healthy Control</strong> oppure <strong>bvFTD</strong>)</li>
<li>probabilità diagnostica associata alla classificazione</li>
</ul>

<p>
La classificazione è basata su feature radiomiche estratte automaticamente da regioni cerebrali segmentate e analizzate tramite modelli supervisionati addestrati su dataset di riferimento.
</p>

<p class="note">
Oltre alla predizione finale, il sistema produce ulteriori indicatori quantitativi utili all’interpretazione clinica assistita.
</p>

</div>
