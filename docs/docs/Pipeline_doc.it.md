# Pipeline Radiomica — MLOps

## Panoramica

La pipeline di neuroimaging è implementata in Nextflow (DSL2) e gira tramite il
pattern **Docker-out-of-Docker (DooD)** all'interno del container `nextflow_worker`.
Trasforma una MRI T1 grezza in una matrice di feature radiomiche strutturata
usata per la diagnosi basata su XGBoost.

---

## File della pipeline

| File | Scopo |
|------|-------|
| `nextflow_worker/nextflow/preprocessing.nf` | Workflow di preprocessing principale (produzione) |
| `nextflow_worker/nextflow/main.nf` | Entry point canonico DSL2 (esecuzioni manuali/CI) |
| `nextflow_worker/nextflow/training.nf` | Workflow di training (offline, ricerca) |
| `nextflow_worker/nextflow/nextflow.config` | Configurazione globale (Docker, params) |
| `nextflow_worker/nextflow/configs/training.config` | Override parametri training |
| `nextflow_worker/nextflow/configs/pyradiomics.yaml` | Impostazioni estrazione radiomica |
| `nextflow_worker/nextflow/configs/hyperparameters.yaml` | Iperparametri nested CV |

---

## Pipeline di preprocessing

### Flusso completo

```
Input: scan.nii.gz (MRI T1)
    │
    ▼ [1] freesurfer / fastsurfer / mock_freesurfer
        Container: clinical-freesurfer (o deepmi/fastsurfer:cuda-v2.4.2)
        Output: nu.mgz (cervello normalizzato) + aparc+aseg.mgz (78 label)
        Tempo:  6–8h (CPU FreeSurfer) | 20–30m (GPU FastSurfer) | 30s (mock)
    │
    ▼ [2] nifti_converter
        Container: clinical-freesurfer (mri_convert)
        Output: nu.nii + aparc+aseg.nii
        Tempo:  < 1 minuto
    │
    ▼ [3] roi_creator
        Container: clinical-fsl (fslmaths)
        Output: ROI/{nome_roi}.nii.gz × 78 maschere binarie
        Tempo:  2–5 minuti
    │
    ▼ [4] csv_collector
        Container: clinical-pyradiomics
        Output: {nome_roi}.csv × 78 (coppie path immagine/maschera)
        Tempo:  < 1 minuto
    │
    ▼ [5] feature_extraction
        Container: clinical-pyradiomics (pyradiomics)
        Output: {nome_roi}_feat.csv × 78 + radiomics_features.csv (aggregato)
        Tempo:  30–60 minuti (4 worker paralleli)
    │
    ▼
Output: /shared_data/features/features_{task_id}.csv
        ~6.864 colonne: {nome_ROI}_{feature_pyradiomics}
        (78 ROI × ~88 feature: shape, first-order, GLCM, GLRLM, GLSZM, NGTDM)
```

### Convenzione di denominazione feature

I nomi delle colonne in `radiomics_features.csv` seguono il pattern:
```
{nome_ROI}_{categoria_feature}_{nome_feature}
```

Esempi:
- `Hippocampus_original_shape_Volume`
- `Amygdala_original_firstorder_Mean`
- `FrontalLobe_original_glcm_Contrast`

---

## Dettaglio processi

### [1] Segmentazione cerebrale

Tre opzioni:

**FreeSurfer** (`brain_segmenter=freesurfer`):
Esegue `recon-all` completo con 16 thread OpenMP. CPU-based, 6–8 ore.

**FastSurfer** (`brain_segmenter=fastsurfer`):
Segmentazione deep learning accelerata GPU. ~10× più veloce di FreeSurfer.

**mock_freesurfer** (`test_mode=true`):
Genera anatomia sintetica via Python/numpy (sfere concentriche, label 1–78).
Completa in ~30 secondi. Usato per test CI e sviluppo.

### [3] Creazione ROI

Per ciascuna delle 78 ROI in `ROI_labels.tsv`:
```bash
fslmaths aparc+aseg.nii -thr {id_label} -uthr {id_label} -bin ROI/{nome_roi}.nii.gz
```

### [5] Estrazione feature

PyRadiomics estrae ~88 feature per ROI. Lo script `aggregate.py` combina
i 78 file `{nome_roi}_feat.csv` in un unico `radiomics_features.csv`.

---

## mock_freesurfer (Modalità Test)

Il processo `mock_freesurfer` è stato aggiunto per abilitare test rapidi della
pipeline senza attendere 6–8 ore per la segmentazione FreeSurfer reale.

**Catena di propagazione:**
`orchestrator/.env (TEST_MODE=true)` → `pipeline.py` → `NextflowRunner` →
`nextflow_worker/main.py` → `nextflow run --test_mode true` → `mock_freesurfer`

**Nota:** Groovy interpreta la stringa `"false"` come truthy. Il flag viene
passato solo quando `test_mode=True` in Python per evitare questo bug.

---

## Pipeline di training

```bash
nextflow run training.nf -c configs/training.config \
  --feat_output /shared_data/nf_output/features \
  --config configs/hyperparameters.yaml
```

Passi di training:
1. `aggregate_features` → `feat_all.csv` (merge_radiomics.r)
2. `select_features` → selezione feature LASSO/RFE
3. `parallel_training` → SVM, RF, kNN, XGBoost in parallelo
4. `frequency_stability` → analisi stabilità importanza feature
5. `aggregate_metrics` → riepilogo metriche cross-validation

Il modello XGBoost è salvato come **extended model** contenente:
- `$booster` — raw xgb.Booster (nessuna dipendenza mlr)
- `$trainingData` — training set per spazio UMAP storico
- `$x`, `$y` — matrice feature ed etichette

---

## Performance misurate (sub-01_ses-test_T1w.nii)

| Step | Modalità | Durata |
|------|---------|--------|
| mock_freesurfer | test_mode=true | ~30 secondi |
| nifti_converter | — | ~10 secondi |
| roi_creator (78 ROI) | FSL | ~3 minuti |
| feature_extraction | 4 worker | ~8 minuti |
| Inferenza R + UMAP | — | ~45 secondi |
| **Totale (modalità test)** | — | **~12 minuti** |
| **Totale (FreeSurfer CPU)** | recon-all | **~4–10 ore** |
