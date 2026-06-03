# Changelog e Analisi Performance
**Data:** 2026-06-02  
**Branch:** main  
**Commit corrente:** b08aab0  
**Commit precedente:** af12851  

---

## PARTE 1 — DIFF COMPLETO (HEAD~1 → HEAD)

### FILE MODIFICATI

```
┌──────────────────────────────────────────────────────────┬───────────┬────────────────────────────────────┐
│ File                                                     │ Righe +/- │ Tipo modifica                      │
├──────────────────────────────────────────────────────────┼───────────┼────────────────────────────────────┤
│ nextflow_worker/nextflow/preprocessing.nf                │ +75 -5    │ Nuovo processo mock_freesurfer     │
│ nextflow_worker/nextflow/training.nf                     │ +40 -1    │ Parametri default, fix demograph   │
│ nextflow_worker/nextflow/nextflow.config                 │ +4 -4     │ Fix path licenza DooD              │
│ inference_engine/R/inference_logic.R                     │ +60 -33   │ Fix XGBoost extended model + conf. │
│ model_service/services/inference.py                      │ +31 -10   │ Fallback MLflow → model.rds locale │
│ nextflow_worker/main.py                                  │ +23 -7    │ test_mode API, fix licenza path    │
│ nextflow_worker/ftd_diagnosis/parallel/models/XGBoost.r  │ +22 -1    │ Extended model con trainingData    │
│ nextflow_worker/ftd_diagnosis/util/merge_radiomics.r     │ +17 -12   │ Fix header TSV + init subset NULL  │
│ orchestrator/services/nextflow_runner.py                 │ +8 -6     │ Propagazione test_mode all'API     │
│ orchestrator/core/config.py                              │ +2 -0     │ Aggiunta variabile TEST_MODE       │
│ orchestrator/main.py                                     │ +4 -0     │ Aggiunta rotta GET /               │
│ orchestrator/services/pipeline.py                        │ +3 -2     │ Passa test_mode al Nextflow runner │
│ docker-compose.yml                                       │ +6 -1     │ Porta API, VITE_AUTH_URL, NF_SET.. │
│ nextflow_worker/docker-compose.yml                       │ +3 -3     │ Rename immagini → clinical-*       │
│ frontend/src/components/clinical/TaskHistory.jsx         │ +3 -2     │ Fix parsing filename MD5 prefix    │
│ inference_engine/api.R                                   │ +3 -0     │ Aggiunta rotta GET /health         │
│ llm_service/main.py                                      │ +4 -0     │ Aggiunta rotta GET / separata      │
│ model_service/main.py                                    │ +4 -0     │ Aggiunta rotta GET / separata      │
└──────────────────────────────────────────────────────────┴───────────┴────────────────────────────────────┘
```

Totale: **22 file modificati — 741 righe aggiunte, 313 rimosse**

---

### FILE CREATI EX-NOVO (untracked)

- `nextflow_worker/nextflow/main.nf` — entrypoint unificato Nextflow (preprocessing + training in sequenza)
- `nextflow_worker/nextflow/configs/hyperparameters_small.yaml` — configurazione ridotta per test veloci
- `nextflow_worker/nextflow/configs/training.config` — override parametri training per Nextflow
- `check_model.R`, `debug_feat.R`, `list_pkgs.R` — script di debug/diagnosi R (non in produzione)
- `train_rf_direct.R`, `train_xgb_direct.R`, `train_xgb_final.R` — script di training diretto (debug)
- `docs/TECHNICAL_REPORT.md` — report tecnico della tesi

---

### DETTAGLIO MODIFICHE SIGNIFICATIVE

#### 1. `preprocessing.nf` — Processo `mock_freesurfer`

**Prima:** Il workflow chiamava direttamente `freesurfer()` o `fastsurfer()`. Non esisteva alcun bypass.

**Dopo:** Aggiunto parametro `params.test_mode = false`. Se `true`, il workflow chiama `mock_freesurfer()` invece di `freesurfer()`.

Il processo mock:
- Usa `mri_convert` per convertire il NIfTI input in `nu.mgz` (ms, non ore)
- Genera `aparc+aseg.mgz` con uno script Python inline: crea 78 label concentriche sferiche senza eseguire `recon-all`
- Produce output strutturalmente identico al FreeSurfer reale, compatibile con tutti i processi downstream (`nifti_converter`, `roi_creator`, `feature_extraction`)

Aggiunto anche fallback per `subject_id`: se il filename non matcha il pattern NIFD, usa il nome file senza estensione invece di restituire `null`.

**Perché:** Permette di testare l'intera pipeline (radiomics → inference → UMAP) senza aspettare 2-8h di segmentazione corticale.

---

#### 2. `training.nf` — Default parameters e fix demograph

**Prima:** Nessun default nei parametri; il canale `demographic_ch` usava `fromPath("NULL")`, che Nextflow interpreta come path e fallisce se il file non esiste.

**Dopo:** 
- Aggiunti 20+ parametri default (brain_segmenter, experiment_name, scripts R, paths, ecc.) — il file è ora auto-documentante e usabile senza config esterna
- `demographic_ch` ora usa `channel.value("NULL")` quando `params.demographic_data` è null, evitando il fallimento su path inesistente
- Il processo `aggregate_features` ora dichiara `demograph` come `val` invece di `path` (coerente con il valore sentinella)
- Rimosso `containerOptions "--env-file ${env}"` da `parallel_training` (il file .env viene ora passato come `path`)

---

#### 3. `nextflow.config` — Fix path licenza in DooD

**Prima:** `runOptions = "-v ${baseDir}/license.txt:/app/license.txt"` — monta la licenza dal path del container Nextflow.

**Dopo:** `runOptions = "-v /tmp/nextflow_work/license.txt:/app/license.txt"` — usa il path host `/tmp/nextflow_work/license.txt`, che è un bind-mount esplicito host↔container (dichiarato in docker-compose). In architettura DooD (Docker-out-of-Docker) il daemon Docker dell'host interpreta i path del `runOptions` come path host, non container.

**Perché:** Il vecchio path `${baseDir}` era valido solo dentro il container Nextflow, non nel daemon host che avvia i container figli.

---

#### 4. `inference_logic.R` — Supporto extended model XGBoost

**Prima:** L'inferenza gestiva solo `xgb.Booster` diretto o modelli caret standard. Il fallback era un singolo `tryCatch` non annidato. Le etichette di output erano `"Malato"/"Sano"` (hardcoded). La risposta non includeva la confidenza.

**Dopo:**
- **Caso 1:** Extended model (oggetto lista con `$booster` + `$mlr_model` + `$trainingData` + `$y`) — prodotto dalla nuova versione di XGBoost.r
- **Caso 2:** `xgb.Booster` diretto (retrocompatibilità)
- **Caso 3:** Modelli caret standard (RF, SVM, kNN)
- Fix etichette: `"bvFTD"/"HC"` invece di `"Malato"/"Sano"`
- Aggiunto campo `confidenza` nella risposta (probabilità della classe predetta)
- Fix `roi_labels`: `read.table(..., header=TRUE, sep="\t")` e colonna `$Label` invece di `header=FALSE` e `$V3`
- `tryCatch` annidato nel fallback per loggare errori invece di crashare silenziosamente

---

#### 5. `model_service/services/inference.py` — Fallback MLflow

**Prima:** Se MLflow non era raggiungibile, l'eccezione propagava e il task falliva.

**Dopo:** Se `get_champion_uri()` lancia un'eccezione, viene cercato `model.rds` in tre path locali:
1. `SHARED_VOLUME_DIR/models/{model_name}/model.rds`
2. `/app/model.rds`
3. `SHARED_VOLUME_DIR/models/model.rds`

Se nessuno esiste, l'errore è esplicito con i path cercati.

---

#### 6. `XGBoost.r` — Extended model serializzato

**Prima:** `saveRDS(xgb_model, "xgb.rds")` — salva solo il `WrappedModel` mlr. `inference_logic.R` non poteva accedere al `xgb.Booster` raw né ai dati di training per il UMAP.

**Dopo:** Salva un oggetto lista esteso:
```r
extended_model <- list(
    trainingData = training_with_outcome,  # dati training per UMAP storico
    x            = as.matrix(best_train_x), # matrice feature
    y            = training_with_outcome$.outcome, # factor "HC"/"bvFTD"
    mlr_model    = xgb_model,              # WrappedModel mlr
    booster      = xgb_model$learner.model # xgb.Booster raw per predizione diretta
)
```

Il modello viene salvato sempre come `xgb.rds` (non rinominato) e loggato su MLflow.

---

#### 7. `merge_radiomics.r` — Fix TSV header e init subset

**Prima:** `read.table(..., header=FALSE, sep="")` → colonna `$V3`. `subset` inizializzato con `data.frame(TargetClass=class)` prima del loop, causando dimensione errata se la prima ROI aveva 0 righe.

**Dopo:** `read.table(..., header=TRUE, sep="\t")` → colonna `$Label`. `subset` inizializzato a `NULL` e creato solo alla prima ROI valida (con righe), evitando l'errore di dimensione.

---

#### 8. `docker-compose.yml` — Fix rete e variabili

**Prima:** `api_gateway` esposta su `0.0.0.0:8000`. Frontend senza `VITE_AUTH_URL`. Nessuna dipendenza `nextflow_worker` → `api_gateway`.

**Dopo:**
- Porta `api_gateway`: `127.0.0.1:8006:8000` (loopback, riduzione superficie di attacco)
- `VITE_AUTH_URL=http://localhost:8006` nel frontend (allineato alla nuova porta)
- `NF_SETTINGS` aggiunto alle env vars di `nextflow_worker`
- `nextflow_worker` ora dipende da `api_gateway` (ordine di avvio corretto)

---

#### 9. `nextflow_worker/docker-compose.yml` — Rename immagini

**Prima:** `freesurfer`, `fsl`, `pyradiomics`

**Dopo:** `clinical-freesurfer`, `clinical-fsl`, `clinical-pyradiomics`

Allineamento con i nomi referenziati in `preprocessing.nf` (`container 'clinical-freesurfer'` ecc.).

---

#### 10. `TaskHistory.jsx` — Fix parsing filename

**Prima:** `firstUnderscoreIndex === 36` — cercava il prefisso UUID a 36 caratteri.

**Dopo:** `firstUnderscoreIndex === 8` — il prefisso è ora un MD5 troncato a 8 caratteri (come prodotto da `orchestrator/routers/analyze.py`).

---

#### 11. Rotte `/health` e `/` unificate

Tutti i servizi Python (`orchestrator`, `llm_service`, `model_service`, `nextflow_worker`) e il servizio R (`inference_engine`) ora espongono sia `GET /` che `GET /health` con `{"status": "ok", "service": "..."}`. Prima alcuni avevano solo `/`, altri nessuna delle due.

---

## PARTE 2 — PERCHÉ PRIMA ~3H, ORA ~15 MINUTI

### Analisi del flusso pipeline preprocessing

Il flusso in `preprocessing.nf` è sequenziale per soggetto:

```
Input NIfTI
    │
    ▼
[1] mock_freesurfer / freesurfer / fastsurfer   ← COLLO DI BOTTIGLIA
    │
    ▼
[2] nifti_converter         (mri_convert ×2, ~5s)
    │
    ▼
[3] roi_creator              (fslmaths ×78 ROI, ~30-60s)
    │
    ▼
[4] csv_collector            (loop bash, ~5s)
    │
    ▼
[5] feature_extraction       (pyradiomics ×78 ROI, --jobs 4, ~5-10min)
```

### Tabella tempi per step

```
┌──────────────────────────┬──────────────┬──────────────┬──────────────────────────────────────────┐
│ Step                     │ Prima        │ Ora          │ Motivo differenza                        │
├──────────────────────────┼──────────────┼──────────────┼──────────────────────────────────────────┤
│ FreeSurfer recon-all     │ 2–8 ore      │ 0            │ Sostituito da mock_freesurfer             │
│ mock_freesurfer          │ (non esist.) │ ~30–60s      │ mri_convert + script Python sferiche     │
│ nifti_converter          │ ~5s          │ ~5s          │ Invariato (mri_convert ×2)               │
│ roi_creator              │ ~30–60s      │ ~30–60s      │ Invariato (fslmaths ×78)                 │
│ csv_collector            │ ~5s          │ ~5s          │ Invariato                                │
│ feature_extraction       │ ~5–10min     │ ~5–10min     │ Invariato (pyradiomics --jobs 4)         │
│ Inference R (inference_  │ ~1–2min      │ ~1–2min      │ Invariato                               │
│ engine)                  │              │              │                                          │
│ UMAP 3D                  │ ~30s         │ ~30s         │ Invariato                               │
│ TOTALE                   │ ~2.5–9.5h    │ ~8–15min     │ Eliminazione recon-all                   │
└──────────────────────────┴──────────────┴──────────────┴──────────────────────────────────────────┘
```

### Spiegazione dettagliata

**Bottleneck eliminato: `recon-all` di FreeSurfer**

`recon-all` è un'analisi strutturale MRI completa che include:
- Normalizzazione intensità, skull-stripping, segmentazione della sostanza bianca/grigia
- Ricostruzione della superficie corticale (pial surface, white surface)
- Parcellazione in ~35 regioni per emisfero con l'atlante Desikan-Killiany
- Pipeline a ~30 stadi sequenziali, non parallelizzabili internamente

Su hardware tipico (16 thread, `-openmp 16`):
- MRI 1mm isotropica 256³: **2–4 ore**
- MRI 3T con `-cw256`: fino a **6–8 ore**

Il mock elimina tutti questi stadi. Produce `nu.mgz` con una semplice conversione formato (1-2 secondi) e `aparc+aseg.mgz` con uno script Python che assegna 78 label via distanza euclidea dal centro (5-10 secondi per un volume 256³).

**Ottimizzazioni aggiuntive rispetto al mock**

1. **Fallback subject_id**: Prima, un NIfTI con nome non-NIFD poteva produrre `subject_id = null`, causando un crash Nextflow prima ancora di avviare FreeSurfer. Il fix `?: filename.replaceAll(...)` evita il fallimento precoce.

2. **`publishDir` con closure `{}`**: Le espressioni `publishDir "${var}"` vengono valutate staticamente da Nextflow; con variabili di processo come `FTD_group` e `subject` è richiesta una closure. Il fix evita path di output errati che potevano portare a riavvii del processo.

3. **`demographic_ch` con `channel.value("NULL")`**: Prima `fromPath("NULL")` causava un errore nel workflow se il file non esisteva, bloccando il processo `aggregate_features`. Ora il workflow parte sempre.

4. **`merge_radiomics.r` fix header**: Prima `header=FALSE, sep=""` leggeva il TSV malformato (tab-separated letto come whitespace-separated), causando errori di colonna in R durante il merge. Il task di training falliva ripetutamente, richiedendo rilanci manuali.

5. **Flag `-resume` di Nextflow**: Il comando `nextflow run ... -resume` (già presente in `nextflow_runner.py`) riutilizza la cache dei processi completati. Con il mock abilitato, se il soggetto è già stato processato (hash NIfTI identico), `mock_freesurfer`, `nifti_converter`, `roi_creator` vengono saltati. Solo `feature_extraction` viene rieseguito se il codice è cambiato. In pratica, la seconda esecuzione sullo stesso file può completare in **< 1 minuto**.

**Step in parallelo**

- `feature_extraction` usa `--jobs 4` (pyradiomics): le 78 ROI vengono processate con 4 worker Python in parallelo. Questo era già presente.
- I processi Nextflow per soggetti diversi (`params.maxforks = 1` per default) sono sequenziali. Con `maxforks > 1` si potrebbero parallelizzare soggetti multipli, ma introduce contesa sulla GPU/CPU.

---

## PARTE 3 — CON DATI REALI COSA CAMBIA

### In produzione (test_mode = false, dati reali)

Con dati reali il bottleneck torna ad essere FreeSurfer/FastSurfer:

```
┌──────────────────────────┬──────────────────┬──────────────────────────────────────────────────────┐
│ Configurazione           │ Tempo stimato    │ Note                                                 │
├──────────────────────────┼──────────────────┼──────────────────────────────────────────────────────┤
│ FreeSurfer recon-all     │ 2–8h/soggetto    │ Dipende da RAM, CPU, risoluzione MRI                 │
│ FastSurfer (CPU)         │ 45–90min/sogg.   │ ~4× più veloce di FreeSurfer su CPU                  │
│ FastSurfer (GPU CUDA)    │ 5–15min/sogg.    │ Richiede GPU ≥ 8GB VRAM; usa MIG se disponibile      │
│ mock_freesurfer          │ ~1min/sogg.      │ Solo per CI/test — output sintetico non diagnostico  │
└──────────────────────────┴──────────────────┴──────────────────────────────────────────────────────┘
```

### Raccomandazioni per ridurre i tempi in produzione

1. **FastSurfer GPU** (`brain_segmenter=fastsurfer`, `fastsurfer_device=cuda`): da 2-8h a 5-15min/soggetto. È il percorso clinico raccomandato per throughput elevato.

2. **`-resume` Nextflow** (già attivo): se un soggetto è già stato segmentato in un run precedente, i processi FreeSurfer/FastSurfer vengono saltati. Solo i processi modificati vengono rieseguiti.

3. **`maxforks > 1`**: per dataset multi-soggetto, aumentare `params.maxforks` permette di segmentare N soggetti in parallelo (CPU-bound). Attenzione: con FastSurfer GPU serve `maxforks=1` per non saturare la VRAM.

4. **Cache features**: `radiomics_features.csv` è salvato in `publishDir "${params.outdir}"`. Se il file esiste già e il soggetto non è cambiato, il `-resume` lo salta automaticamente.

### Impatto del mock sui tempi di sviluppo

Con `TEST_MODE=true` nell'environment dell'orchestrator, l'intera pipeline end-to-end (NIfTI → diagnosi + UMAP) completa in **~10–15 minuti** invece di **~3–9 ore**, permettendo:
- Iterazioni rapide su `inference_logic.R`, `XGBoost.r`, `merge_radiomics.r`
- Test CI automatizzati senza infrastruttura GPU
- Debug della pipeline senza attendere segmentazione reale

Il flag è passato end-to-end: `orchestrator.settings.TEST_MODE` → `pipeline.py` → `nextflow_runner.py` → `nextflow_worker/main.py` → `--test_mode true` al processo Nextflow.

---

*Report generato automaticamente il 2026-06-02*
