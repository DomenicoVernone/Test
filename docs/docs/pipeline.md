<style>

:root {
  --primary: #3f51b5;
  --secondary: #1e3a8a;
  --background-soft: #eef2ff;
  --flow-bg: #f5f6fa;
  --code-bg: #eeeeee;
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
  margin-bottom: 18px;
}

h2 {
  margin-top: 36px;
  margin-bottom: 12px;
  color: var(--secondary);
}

.box {
  border-left: 6px solid var(--primary);
  background: var(--background-soft);
  padding: 20px;
  border-radius: 8px;
  margin: 26px 0;
}

.flow {
  background: var(--flow-bg);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  margin: 22px 0;
  font-size: 1rem;
  letter-spacing: 0.4px;
}

.code {
  background: var(--code-bg);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
}

.section-note {
  margin-top: 12px;
  color: var(--text-soft);
}

ul {
  margin-top: 8px;
}

li {
  margin-bottom: 5px;
}

.highlight {
  font-weight: 600;
  color: var(--secondary);
}

</style>

<h1>Pipeline Neuroimaging</h1>

<div class="box">

<p>
La pipeline neuroimaging implementata in <strong>ClinicalTwin</strong> consente la trasformazione automatizzata di immagini MRI strutturali T1-pesate in rappresentazioni quantitative utilizzabili per la classificazione diagnostica tra
<strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong> e
<strong>Healthy Controls (HC)</strong>.
</p>

<p>
Il workflow computazionale costruisce progressivamente un vettore strutturato di biomarcatori radiomici interpretabili, riproducibili e compatibili con modelli di machine learning supervisionati.
</p>

</div>

<h2>Workflow computazionale</h2>

<div class="flow">

MRI → FreeSurfer → ROI Extraction → Radiomics Features → CSV Dataset → Machine Learning → UMAP Projection

</div>

<h2>Input: immagini MRI strutturali</h2>

<p>
La pipeline riceve in ingresso immagini volumetriche cerebrali T1-pesate nei formati standard:
</p>

<ul>
<li><span class="code">.nii</span></li>
<li><span class="code">.nii.gz</span></li>
</ul>

<p>
Queste immagini costituiscono la base per l’estrazione di biomarcatori morfometrici regionali utilizzati nella classificazione diagnostica automatizzata.
</p>

<p class="section-note">
Prima dell’elaborazione, i dati vengono validati e organizzati per garantire compatibilità con la pipeline di segmentazione FreeSurfer e con lo standard BIDS quando disponibile.
</p>

<h2>Segmentazione anatomica con FreeSurfer</h2>

<p>
La prima fase della pipeline consiste nella segmentazione anatomica cerebrale tramite
<span class="highlight">FreeSurfer</span>, uno strumento ampiamente validato nella neuroimaging analysis strutturale.
</p>

<p>
Il processo produce una rappresentazione dettagliata del cervello suddivisa in regioni neuroanatomiche standardizzate secondo atlanti di riferimento corticali e sottocorticali.
</p>

<h2>Estrazione delle regioni di interesse (ROI)</h2>

<p>
Successivamente vengono identificate automaticamente le
<span class="highlight">Regions of Interest (ROI)</span>
rilevanti per l’analisi delle alterazioni neurodegenerative frontotemporali.
</p>

<p>
Le ROI sono derivate dalle mappe di segmentazione prodotte da FreeSurfer e organizzate secondo strutture neuroanatomiche standardizzate.
</p>

<p class="section-note">
Questa fase consente di isolare le aree cerebrali su cui verranno calcolate le feature radiomiche regionali.
</p>

<h2>Estrazione delle feature radiomiche</h2>

<p>
Una volta definite le ROI, viene eseguita l’estrazione automatizzata delle
<span class="highlight">feature radiomiche</span>
mediante strumenti dedicati (PyRadiomics).
</p>

<p>
Le feature includono descrittori quantitativi di:
</p>

<ul>
<li>intensità voxel-wise</li>
<li>texture regionale</li>
<li>distribuzione statistica dei segnali</li>
<li>proprietà morfometriche locali</li>
</ul>

<p class="section-note">
Questa fase trasforma l’immagine MRI in una rappresentazione numerica ad alta dimensionalità utilizzabile per l’analisi computazionale supervisionata.
</p>

<h2>Generazione del dataset strutturato (CSV)</h2>

<p>
Le feature radiomiche estratte vengono aggregate in una rappresentazione tabellare strutturata in formato
<span class="code">CSV</span>, in cui:
</p>

<ul>
<li>ogni riga rappresenta un soggetto</li>
<li>ogni colonna rappresenta una feature radiomica regionale</li>
</ul>

<p>
Questo dataset costituisce l’input del modello di classificazione supervisionata utilizzato dal sistema ClinicalTwin.
</p>

<p class="section-note">
La standardizzazione del formato consente l’integrazione con moduli di inferenza indipendenti dalla pipeline di preprocessing.
</p>

<h2>Classificazione tramite modello di Machine Learning</h2>

<p>
Il vettore di feature radiomiche viene elaborato da un modello supervisionato addestrato per distinguere tra:
</p>

<ul>
<li><strong>Healthy Control (HC)</strong></li>
<li><strong>behavioral variant Frontotemporal Dementia (bvFTD)</strong></li>
</ul>

<p>
Il modello restituisce:
</p>

<ul>
<li>classe predetta</li>
<li>probabilità diagnostica associata</li>
<li>posizionamento del soggetto nello spazio delle feature</li>
</ul>

<p class="section-note">
Questa fase rappresenta il nucleo decisionale del sistema di supporto diagnostico assistito.
</p>

<h2>Proiezione nello spazio latente UMAP</h2>

<p>
Come fase finale della pipeline, i dati radiomici vengono proiettati in uno spazio latente tridimensionale tramite
<span class="highlight">UMAP (Uniform Manifold Approximation and Projection)</span>.
</p>

<p>
Questa trasformazione consente di:
</p>

<ul>
<li>visualizzare la distribuzione dei soggetti nello spazio delle feature</li>
<li>confrontare il profilo del paziente con la popolazione di riferimento</li>
<li>supportare l’interpretazione delle predizioni del modello</li>
<li>abilitare l’esplorazione interattiva tramite dashboard clinica</li>
</ul>

<p class="section-note">
La rappresentazione UMAP costituisce uno strumento di interpretabilità visiva fondamentale per il supporto decisionale assistito nel contesto neurodegenerativo.
</p>
