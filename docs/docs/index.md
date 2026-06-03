# Clinical Twin — FTD Radiomics Platform

**Clinical Twin** is an MLOps platform for the differential diagnosis of
Frontotemporal Dementia (FTD) variants through automated analysis of T1 MRI.

---

## What it does

The system takes a T1 MRI scan as input and produces:

- **Diagnosis**: `HC` (Healthy Control) or `bvFTD` (behavioral variant FTD)
- **Confidence score**: 0–100% (XGBoost probability)
- **3D UMAP visualization**: patient position in the clinical space relative to the training cohort

Total analysis time: **~12 minutes** (test mode) or **~4–10 hours** (full FreeSurfer pipeline).

---

## Architecture

7 containerized microservices orchestrated via Docker Compose:

| Service | Port | Role |
|---------|------|------|
| Frontend (React) | 5173 | Clinical dashboard |
| API Gateway | 127.0.0.1:8006 | JWT authentication |
| Orchestrator | 127.0.0.1:8001 | Task management |
| Model Service | 127.0.0.1:8003 | MLflow + model download |
| Inference Engine | 127.0.0.1:8004 | R + XGBoost + UMAP |
| LLM Service | 127.0.0.1:8002 | AI assistant |
| Nextflow Worker | 127.0.0.1:8005 | Neuroimaging pipeline |

See [System Architecture](SYSTEM_ARCHITECTURE.md) for the complete diagram.

---

## Pipeline

```
T1 MRI (.nii.gz)
    → FreeSurfer recon-all (or mock_freesurfer for testing)
    → 78 brain region masks (FSL fslmaths)
    → PyRadiomics feature extraction (~6,864 features)
    → XGBoost classification + UMAP 3D embedding
    → Diagnosis + confidence + visualization
```

See [Pipeline Documentation](Pipeline_doc.md) for full details.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/carlosto033/Tesi-FTD.git && cd Tesi-FTD

# 2. Configure .env files and add FreeSurfer license
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
# Set SECRET_KEY to the same value in both files
cp /path/to/license.txt nextflow_worker/license.txt

# 3. Build pipeline images
docker compose -f nextflow_worker/docker-compose.yml build

# 4. Enable test mode for fast runs (~12 min instead of ~8h)
echo "TEST_MODE=true" >> orchestrator/.env

# 5. Start
docker compose up --build -d

# 6. Open dashboard
# http://localhost:5173
```

See [Quickstart](Guida_Rapida.md) for the complete walkthrough.

---

## Status

| Component | Status |
|-----------|--------|
| End-to-end pipeline | ✅ Working (tested 2026-05-28) |
| TEST_MODE (mock FreeSurfer) | ✅ Working (~12 min) |
| Full FreeSurfer pipeline | ✅ Working (~4h 21m measured) |
| XGBoost inference + UMAP 3D | ✅ Working (HC, 79.57% on test scan) |
| MLflow/DagsHub model registry | ✅ Working (with fallback) |
| Current model | ⚠️ Trained on 12 synthetic subjects — research only |
| Clinical validation | ❌ Requires real NIFD dataset |

---

## Documentation

- [System Architecture](SYSTEM_ARCHITECTURE.md) — service diagram, DooD, shared volume
- [Components & Structure](COMPONENTS_&_STRUCTURE.md) — directory structure, file roles
- [Installation](Installazione.md) — prerequisites, setup steps
- [Configuration](Configurazione.md) — .env variables, TEST_MODE, GPU config
- [Pipeline](Pipeline_doc.md) — Nextflow processes, mock_freesurfer, training
- [Quickstart](Guida_Rapida.md) — run your first analysis
- [API Reference](api.md) — all endpoints with curl examples
- [Deployment](Deployment.md) — Docker commands, DooD, troubleshooting
- [Testing](testing.md) — test results, bug fixes, known limitations
- [Technical Report](REPORT_FINALE_COMPLETO.md) — complete session report
- [Changelog](CHANGES_AND_PERFORMANCE.md) — diff and performance data
