# Radiomics Pipeline — MLOps

## Overview

The neuroimaging pipeline is implemented in Nextflow (DSL2) and runs via the
**Docker-out-of-Docker (DooD)** pattern inside the `nextflow_worker` container.
It transforms a raw T1 MRI into a structured radiomic feature matrix
used for XGBoost-based diagnosis.

---

## Pipeline Files

| File | Purpose |
|------|---------|
| `nextflow_worker/nextflow/preprocessing.nf` | Main preprocessing workflow (production) |
| `nextflow_worker/nextflow/main.nf` | Canonical DSL2 entry point (manual/CI runs) |
| `nextflow_worker/nextflow/training.nf` | Training workflow (offline, research) |
| `nextflow_worker/nextflow/nextflow.config` | Global configuration (Docker, params) |
| `nextflow_worker/nextflow/configs/training.config` | Training-specific parameter overrides |
| `nextflow_worker/nextflow/configs/pyradiomics.yaml` | PyRadiomics extraction settings |
| `nextflow_worker/nextflow/configs/hyperparameters.yaml` | Nested CV hyperparameters |

---

## Preprocessing Pipeline

### Full Flow

```
Input: scan.nii.gz (T1 MRI)
    │
    ▼ [1] freesurfer / fastsurfer / mock_freesurfer
        Container: clinical-freesurfer (or deepmi/fastsurfer:cuda-v2.4.2)
        Input:  scan.nii.gz
        Output: {subject}/mri/nu.mgz        (intensity normalized brain)
                {subject}/mri/aparc+aseg.mgz (anatomical parcellation, 78 labels)
        Time:   6–8h (CPU FreeSurfer) | 20–30m (GPU FastSurfer) | 30s (mock)
    │
    ▼ [2] nifti_converter
        Container: clinical-freesurfer (mri_convert)
        Input:  nu.mgz + aparc+aseg.mgz
        Output: nu.nii + aparc+aseg.nii
        Time:   < 1 minute
    │
    ▼ [3] roi_creator
        Container: clinical-fsl (fslmaths)
        Input:  aparc+aseg.nii + ROI_labels.tsv (78 ROI definitions)
        Output: ROI/{roi_name}.nii.gz  × 78 binary masks
        Time:   2–5 minutes
    │
    ▼ [4] csv_collector
        Container: clinical-pyradiomics
        Input:  nu.nii + ROI/*.nii.gz + ROI_labels.tsv
        Output: {roi_name}.csv × 78 (image/mask path pairs)
        Time:   < 1 minute
    │
    ▼ [5] feature_extraction
        Container: clinical-pyradiomics (pyradiomics)
        Input:  {roi_name}.csv × 78
        Output: {roi_name}_feat.csv × 78 + radiomics_features.csv (aggregated)
        Time:   30–60 minutes (4 parallel workers)
    │
    ▼
Output: /shared_data/features/features_{task_id}.csv
        ~6,864 columns: {ROI_name}_{pyradiomics_feature}
        (78 ROIs × ~88 features: shape, first-order, GLCM, GLRLM, GLSZM, NGTDM)
```

### Feature Naming Convention

Column names in `radiomics_features.csv` follow the pattern:
```
{ROI_name}_{feature_category}_{feature_name}
```

Examples:
- `Hippocampus_original_shape_Volume`
- `Amygdala_original_firstorder_Mean`
- `FrontalLobe_original_glcm_Contrast`

ROI names are sourced from `ROI_labels.tsv` (78 brain regions).

---

## Process Detail

### [1] Brain Segmentation

Three options:

**FreeSurfer** (`brain_segmenter=freesurfer`):
```bash
recon-all -subject {subject} -i {nifti} -all -notal-check -cw256 -openmp 16
```
Produces `aparc+aseg.mgz` with 78 anatomical labels matching `ROI_labels.tsv`.

**FastSurfer** (`brain_segmenter=fastsurfer`):
```bash
run_fastsurfer.sh --t1 {nifti} --sid {subject} --fsaparc --device cuda
```
GPU-accelerated deep learning segmentation, ~10× faster than FreeSurfer.

**mock_freesurfer** (`test_mode=true`):
Generates synthetic anatomy via Python/numpy (concentric spheres, labels 1–78).
Used for CI testing and pipeline development. Completes in ~30 seconds.
Activate via `TEST_MODE=true` in `orchestrator/.env`.

### [3] ROI Creation

For each of the 78 ROIs in `ROI_labels.tsv`:
```bash
fslmaths aparc+aseg.nii -thr {label_id} -uthr {label_id} -bin ROI/{roi_name}.nii.gz
```

The `ROI_labels.tsv` format (tab-separated, with header):
```
Index	Label
1	Left-Cerebral-White-Matter
2	Left-Cerebral-Cortex
...
78	Right-Cerebral-Cortex
```

### [5] Feature Extraction

PyRadiomics extracts ~88 features per ROI using the settings in `pyradiomics.yaml`.
The `aggregate.py` script inside the `feature_extraction` process combines all
78 `{roi_name}_feat.csv` files into a single `radiomics_features.csv`.

---

## mock_freesurfer (Test Mode)

The `mock_freesurfer` process was added to enable rapid pipeline testing
without waiting 6–8 hours for real FreeSurfer segmentation.

```groovy
// Activation: params.test_mode = true
process mock_freesurfer {
    container 'clinical-freesurfer'
    // Converts input NIfTI to nu.mgz
    // Generates aparc+aseg.mgz with 78 concentric sphere labels via Python/numpy
    // Completes in ~30 seconds
}
```

**Propagation chain:**
`orchestrator/.env (TEST_MODE=true)` → `pipeline.py` → `NextflowRunner` →
`nextflow_worker/main.py` → `nextflow run --test_mode true` → `mock_freesurfer`

**Important:** Groovy interprets the string `"false"` as truthy.
The flag is only passed when `test_mode=True` in Python to avoid this.

---

## Training Pipeline

The training pipeline (`training.nf`) is run **offline** to produce the `.rds` model
that gets deployed to `inference_engine`.

```bash
# Build training image
docker compose -f nextflow_worker/docker-compose.yml build ftd_training

# Run training (requires preprocessed feature CSVs)
nextflow run training.nf -c configs/training.config \
  --feat_output /shared_data/nf_output/features \
  --config configs/hyperparameters.yaml
```

Training steps:
1. `aggregate_features` → `feat_all.csv` (merge_radiomics.r)
2. `select_features` → LASSO/RFE feature selection (features_selection.r)
3. `parallel_training` → SVM, RF, kNN, XGBoost in parallel
4. `frequency_stability` → feature importance stability analysis
5. `aggregate_metrics` → cross-validation metrics summary

The XGBoost model is saved as an **extended model** containing:
- `$booster` — raw xgb.Booster (no mlr dependency)
- `$trainingData` — training set for UMAP historical space
- `$x`, `$y` — feature matrix and labels

---

## ROI Labels File

`nextflow_worker/data/external/ROI_labels.tsv` — 78 brain regions.

Critical: both `merge_radiomics.r` and `inference_logic.R` must parse this file
with `header=TRUE, sep="\t"` (a historical bug where `header=FALSE, sep=""` caused
all ROI mappings to be wrong was fixed in session 2026-05-27).

---

## Measured Performance (sub-01_ses-test_T1w.nii)

| Step | Mode | Duration |
|------|------|---------|
| mock_freesurfer | test_mode=true | ~30 seconds |
| nifti_converter | — | ~10 seconds |
| roi_creator (78 ROIs) | FSL | ~3 minutes |
| feature_extraction | 4 workers | ~8 minutes |
| R inference + UMAP | — | ~45 seconds |
| **Total (test mode)** | — | **~12 minutes** |
| **Total (FreeSurfer CPU)** | recon-all | **~4–10 hours** |
