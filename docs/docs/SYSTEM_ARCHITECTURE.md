# System Architecture — MLOps

## Overview

MLOps is a distributed platform for the differential diagnosis of
Frontotemporal Dementia (FTD) variants based on radiomics of T1 MRI.
The system follows a microservices architecture with 7 containerized services
orchestrated via Docker Compose.

---

## Service Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    clinical_twin_net (bridge)                    │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   frontend   │    │   api_gateway    │    │  llm_service  │  │
│  │  React/Vite  │    │  FastAPI + JWT   │    │ FastAPI + LLM │  │
│  │  port: 5173  │    │  port: 8006(h)   │    │ port: 8002(h) │  │
│  └──────┬───────┘    └────────┬─────────┘    └───────────────┘  │
│         │                    │                                   │
│         │            ┌───────▼──────────┐                       │
│         └───────────►│   orchestrator   │                       │
│                      │    FastAPI       │                       │
│                      │  port: 8001(h)   │                       │
│                      └──┬──────────┬───┘                       │
│                         │          │                            │
│              ┌──────────▼──┐  ┌────▼────────────┐             │
│              │model_service│  │nextflow_worker  │             │
│              │FastAPI+MLflow│  │ FastAPI+Nextflow │             │
│              │port: 8003(h)│  │  port: 8005(h)  │             │
│              └──────┬───────┘  └────────┬────────┘             │
│                     │                   │ DooD                  │
│              ┌──────▼────────┐    ┌─────▼──────────────────┐  │
│              │inference_engine│   │  Docker daemon (HOST)   │  │
│              │  R + Plumber   │   │  clinical-freesurfer    │  │
│              │ port: 8004(h)  │   │  clinical-fsl           │  │
│              └────────────────┘   │  clinical-pyradiomics   │  │
│                                   │  ftd-training           │  │
│                                   └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

(h) = host port on 127.0.0.1 loopback
```

---

## Services Detail

| Service | Technology | Port (host) | Role |
|---------|-----------|-------------|------|
| `frontend` | React 18 + Vite + TailwindCSS | 5173 | Clinical dashboard: MRI upload, task history, 3D UMAP visualization |
| `api_gateway` | FastAPI + SQLite | 127.0.0.1:8006 | JWT authentication, user management |
| `orchestrator` | FastAPI + SQLite | 127.0.0.1:8001 | Async task management, pipeline coordination |
| `model_service` | FastAPI + MLflow | 127.0.0.1:8003 | Champion model download from DagsHub, trigger R inference |
| `inference_engine` | R + Plumber + uwot | 127.0.0.1:8004 | XGBoost inference, 3D UMAP embedding computation |
| `llm_service` | FastAPI + Claude/Groq | 127.0.0.1:8002 | AI clinical interpretation assistant |
| `nextflow_worker` | FastAPI + Nextflow | 127.0.0.1:8005 | Neuroimaging pipeline coordinator (DooD) |

---

## End-to-End Data Flow

```
User (browser)
    │ HTTP POST multipart (NIfTI file)
    ▼
Frontend :5173
    │ POST /analyze/upload + JWT
    ▼
API Gateway :8006  ──► validates JWT
    │
    ▼
Orchestrator :8001
    │  Phase 0: GET /model_info/HC_vs_bvFTD → brain_segmenter tag
    │  Phase 1: POST /start_preprocessing → nextflow_worker
    │  Phase 2: POST /infer → model_service
    │
    ├──► Nextflow Worker :8005
    │        │ subprocess: nextflow run preprocessing.nf
    │        │ DooD: Docker daemon spawns 4 containers on HOST
    │        │
    │        ├── clinical-freesurfer: recon-all (6–8h CPU / 30s mock)
    │        │       Output: nu.mgz + aparc+aseg.mgz
    │        ├── clinical-freesurfer: mri_convert
    │        │       Output: nu.nii + aparc+aseg.nii
    │        ├── clinical-fsl: fslmaths × 78
    │        │       Output: ROI/*.nii.gz (78 brain region masks)
    │        └── clinical-pyradiomics: pyradiomics × 78
    │               Output: radiomics_features.csv (~6864 features)
    │                      → /shared_data/features/features_17.csv
    │
    └──► Model Service :8003
             │ Download xgb.rds from DagsHub MLflow (or local fallback)
             │ POST /infer → inference_engine
             ▼
         Inference Engine :8004 (R/Plumber)
             │ Load XGBoost model (.rds)
             │ Load features_17.csv
             │ Align 6864 features via ROI mapping
             │ Predict: HC or bvFTD + confidence
             │ Compute UMAP 3D (training set + new patient)
             │ Write result_17.json → /shared_data/results/
             ▼
         Result: {"diagnosi_predetta": "HC", "confidenza": 0.7957, "plot_data": {...}}
             │
             ▼
Orchestrator :8001  ──► task status = COMPLETED (100%)
    │
    ▼
Frontend :5173  ──► polls GET /analyze/status/17 every 3s
    ▼
User sees: diagnosis + confidence + 3D UMAP visualization
```

---

## DooD (Docker-out-of-Docker)

The `nextflow_worker` uses the **Docker-out-of-Docker** pattern:
it mounts the host Docker socket (`/var/run/docker.sock`) to spawn
pipeline containers directly on the **host Docker daemon**.

```yaml
# docker-compose.yml (nextflow_worker)
volumes:
  - /var/run/docker.sock:/var/run/docker.sock  # DooD
  - /tmp/nextflow_work:/tmp/nextflow_work       # shared work directory
```

**Critical implication:** all bind-mount paths in Nextflow processes
must be **host filesystem paths**, not container-internal paths.
The path `/tmp/nextflow_work` exists on both host and container
(via the bind-mount), making it the coordination point for:
- FreeSurfer license: `main.py` copies it to `/tmp/nextflow_work/license.txt`
- Nextflow work directory: isolated per task with hash-based subdirs

---

## Shared Volume: clinical_twin_shared_data

Named Docker volume mounted at `/shared_data` in all services.

```
/shared_data/
├── nifti/                          # Uploaded MRI files
│   └── {8char_md5}_{filename}.nii
├── features/                       # Radiomic feature CSVs
│   └── features_{task_id}.csv
├── results/                        # Inference results
│   └── result_{task_id}.json
├── models/                         # Downloaded MLflow models
│   └── HC_vs_bvFTD/
│       └── model.rds
└── ROI_labels.tsv                  # Copied by nextflow_worker at boot
```

---

## MLflow / DagsHub Integration

```
Training (offline, XGBoost.r):
    nested CV → best fold model → extended_model.rds
    → mlflow_log_artifact("xgb.rds", "model")
    → registered as HC_vs_bvFTD@champion on DagsHub

Inference (online, model_service):
    MlflowClient.search_registered_models("HC_vs_bvFTD")
    → model.aliases["champion"] → version → run_id → download .rds
    → Fallback: /app/model.rds (local bind-mount)
```

The **extended model** format (saved by `XGBoost.r`) contains:
- `$booster`: raw `xgb.Booster` (no `mlr` dependency — inference_engine has only `xgboost`)
- `$trainingData`: training set with `.outcome` factor (HC/bvFTD) for UMAP historical space
- `$x`: feature matrix for UMAP fitting
- `$y`: class labels

---

## Network Security

All services bind on the internal Docker network `clinical_twin_net`.
External access via host-bound ports is restricted to loopback:

```
api_gateway  → 127.0.0.1:8006  (not 0.0.0.0:8006)
orchestrator → 127.0.0.1:8001
...
```

This prevents external network access without a reverse proxy (nginx/caddy).
The frontend on port `5173` is the only service accessible without loopback restriction
(intentional: it serves the static UI to local browsers).

---

## Database

SQLite database at `/shared_db/clinical_twin.db`, mounted as a named volume
`clinical_twin_db` shared between `api_gateway` and `orchestrator`.

Tables:
- `users`: username, hashed password (bcrypt)
- `tasks`: id, filename, status, progress, model_name, created_at, updated_at
