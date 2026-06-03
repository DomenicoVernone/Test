# Testing — Clinical Twin

---

## Test Summary

All tests were executed on the `main` branch (commit `b08aab0`).

| Test | Mode | Status | Duration | Result |
|------|------|--------|---------|--------|
| Pipeline (synthetic data) | TEST_MODE=true | ✅ PASSED | ~12 min | HC, 79.57% |
| Full pipeline (real MRI) | FreeSurfer CPU | ✅ PASSED | ~4h 21m | HC, 79.57% |
| MLflow fallback | No DagsHub connection | ✅ PASSED | — | Local model used |
| Mock runner (USE_MOCK) | USE_MOCK=true | ✅ PASSED | ~2 min | Synthetic CSV |

---

## Test 1: Synthetic Pipeline (TEST_MODE=true)

**Purpose:** Verify the full pipeline without waiting for FreeSurfer (~8h).

**Setup:**
```env
# orchestrator/.env
TEST_MODE=true
USE_MOCK=false
```

**Input:** `sub-01_ses-test_T1w.nii` (real T1 MRI)

**Execution:**
```bash
docker compose up --build -d

curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

TOKEN=$(curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sub-01_ses-test_T1w.nii" \
  -F "model_name=HC_vs_bvFTD"
```

**Results (Task 17):**
```json
{
  "status": "COMPLETED",
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [12 points — 6 HC + 6 bvFTD],
    "nuovo_paziente": {"x": ..., "y": ..., "z": ...}
  }
}
```

**Timeline:**
- `mock_freesurfer`: ~30 seconds
- `nifti_converter`: ~10 seconds
- `roi_creator` (78 ROIs): ~3 minutes
- `feature_extraction` (4 workers): ~8 minutes
- R inference + UMAP 3D: ~45 seconds
- **Total: ~12 minutes**

---

## Test 2: Real MRI (FreeSurfer CPU)

**Input:** `sub-01_ses-test_T1w.nii` (same file, TEST_MODE=false)

**Configuration:** `TEST_MODE=false`, `brain_segmenter=freesurfer`

**Results:** Same as Test 1 (HC, 79.57%) — consistent between mock and real FreeSurfer segmentation for this scan.

**Timeline:**
- FreeSurfer `recon-all`: 4 hours 21 minutes
- Remaining steps: ~12 minutes
- **Total: ~4 hours 33 minutes**

---

## Bug Fixes Applied During Testing

20 bugs were identified and fixed across 2 development sessions. Summary:

### Root Cause Categories

| Category | Bug count | Impact |
|----------|-----------|--------|
| ROI_labels.tsv parsing (`header=FALSE, sep=""`) | 2 | All ROI mappings wrong → zero features → meaningless predictions |
| DooD path misalignment (FreeSurfer license) | 3 | FreeSurfer crash at launch |
| Docker image name mismatch | 1 | All Nextflow processes impossible to start |
| XGBoost model format incompatible with inference_engine | 1 | Inference always crashed |
| `cbind` row count mismatch (multi-subject) | 1 | Training impossible on real datasets |
| `test_mode` propagation chain broken | 3 | Mock mode never activated despite setting `TEST_MODE=true` |
| Missing tryCatch nesting | 1 | HTTP 500 instead of graceful "Sconosciuto" fallback |
| Hardcoded clinical labels ("Malato"/"Sano") | 1 | Wrong clinical labels in output |
| Filename display parsing (UUID vs MD5[:8]) | 1 | Task list showed garbled filenames |

### Critical Fixes (P1)

**1. ROI labels parsing** (`merge_radiomics.r`, `inference_logic.R`):
```r
# Before (broken):
roi <- read.table(path, header = FALSE, sep = "")
roi_names <- roi$V3   # column doesn't exist

# After (fixed):
roi <- read.table(path, header = TRUE, sep = "\t")
roi_names <- roi$Label
```

**2. FreeSurfer license path** (`nextflow.config`, `main.py`):
```groovy
# Before: ${baseDir}/license.txt (container-internal path, not visible to host Docker daemon)
# After:  /tmp/nextflow_work/license.txt (host path via bind-mount)
runOptions = "-v /tmp/nextflow_work/license.txt:/app/license.txt"
```

**3. Docker image names** (`nextflow_worker/docker-compose.yml`):
```yaml
# Before: image: freesurfer (not found by Nextflow)
# After:  image: clinical-freesurfer (matches preprocessing.nf)
```

**4. XGBoost extended model** (`XGBoost.r`):
```r
# Before: saveRDS(xgb_model, "xgb.rds")  # requires mlr to deserialize
# After:  saveRDS(list(booster=xgb_model$learner.model,
#                      trainingData=best_train_x, ...), "xgb.rds")
```

---

## How to Repeat the Tests

### Quick test (TEST_MODE=true, ~15 min)

```bash
# 1. Set test mode
echo "TEST_MODE=true" >> orchestrator/.env

# 2. Start system
docker compose up --build -d
sleep 30

# 3. Register and login
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

TOKEN=$(curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 4. Upload any NIfTI file
curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your_scan.nii" \
  -F "model_name=HC_vs_bvFTD"

# 5. Poll status (or watch the frontend at http://localhost:5173)
TASK_ID=1
while true; do
  STATUS=$(curl -s http://localhost:8001/analyze/status/$TASK_ID \
    -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "Status: $STATUS"
  [ "$STATUS" = "COMPLETED" ] || [ "$STATUS" = "ERROR" ] && break
  sleep 15
done
```

### Full pipeline test (FreeSurfer real, ~8h)

```bash
# Same as above but with:
echo "TEST_MODE=false" >> orchestrator/.env
docker compose restart orchestrator
```

---

## Known Limitations

### Current model (synthetic training data)

The deployed `HC_vs_bvFTD` model is trained on **12 synthetic subjects**
(6 HC + 6 bvFTD generated from 1 real scan + Gaussian noise).

| Limitation | Impact |
|-----------|--------|
| Training on 12 synthetic subjects | Model does not generalize to real patients |
| No feature selection (LASSO/RFE not applied) | ~6,864 features used without selection |
| Confidence score uncalibrated | 79.57% is not a clinically interpretable probability |
| UMAP space with 12 points | Visualization is not clinically meaningful |
| Binary classification only (HC vs bvFTD) | Other FTD variants not covered (nfvPPA, svPPA, CBS, PSP) |

### Infrastructure

| Limitation | Status |
|-----------|--------|
| Task state in memory (nextflow_worker) | Lost on container restart |
| No HTTPS | HTTP only (add nginx/caddy for production) |
| JWT no refresh token | 30-min sessions, requires re-login |
| No monitoring/alerting | No Prometheus/Grafana integration |
| DICOM not supported | Only NIfTI (.nii/.nii.gz) |

---

## Requirements for Clinical Validation

1. Re-train model on real NIFD dataset (≥200 subjects)
2. Apply LASSO/RFE feature selection
3. Calibrate output probabilities (isotonic regression or Platt scaling)
4. Independent validation cohort
5. Report: sensitivity, specificity, PPV, NPV, AUC-ROC
6. Clinical review by neurologists
7. HIPAA/GDPR compliance review (DICOM anonymization, data encryption)
