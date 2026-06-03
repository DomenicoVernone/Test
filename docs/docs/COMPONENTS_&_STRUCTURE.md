# Components & Project Structure — Clinical Twin

---

## Repository Structure

```
Tesi-FTD/
├── api_gateway/                    # JWT authentication service
│   ├── main.py
│   ├── Dockerfile
│   └── .env.example
│
├── orchestrator/                   # Task management and pipeline coordinator
│   ├── main.py
│   ├── core/
│   │   ├── config.py               # Settings (SECRET_KEY, TEST_MODE, USE_MOCK...)
│   │   └── database.py
│   ├── services/
│   │   ├── pipeline.py             # run_full_pipeline() — 3-phase pipeline
│   │   ├── nextflow_runner.py      # HTTP client for nextflow_worker
│   │   └── mock_runner.py          # MockRunner for USE_MOCK=true
│   ├── routers/
│   │   └── analyze.py              # POST /analyze/upload, GET /analyze/status/{id}
│   ├── Dockerfile
│   └── .env.example
│
├── model_service/                  # MLflow model download + R inference trigger
│   ├── main.py                     # POST /infer, GET /model_info/{name}
│   ├── services/
│   │   └── inference.py            # InferenceOrchestrator (MLflow + fallback)
│   ├── model.rds                   # Fallback local model
│   ├── Dockerfile
│   └── .env.example
│
├── inference_engine/               # R statistical inference (Plumber)
│   ├── api.R                       # GET /health, POST /infer (Plumber router)
│   ├── R/
│   │   └── inference_logic.R       # XGBoost inference + UMAP 3D computation
│   ├── model.rds                   # Fallback local model
│   └── Dockerfile
│
├── llm_service/                    # AI clinical assistant
│   ├── main.py
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                       # React clinical dashboard
│   ├── src/
│   │   ├── components/clinical/
│   │   │   ├── TaskHistory.jsx     # Task list sidebar (polling + LiveTimer)
│   │   │   ├── UmapViewer.jsx      # 3D UMAP visualization
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   └── useTaskPolling.js   # Auto-refresh task status
│   │   └── services/
│   │       └── api.js
│   └── Dockerfile
│
├── nextflow_worker/                # Neuroimaging pipeline worker (DooD)
│   ├── main.py                     # FastAPI: POST /start_preprocessing, GET /status/{id}
│   ├── nextflow/
│   │   ├── preprocessing.nf        # Main pipeline: segmentation → radiomics
│   │   ├── training.nf             # Training pipeline: merge → select → train
│   │   ├── main.nf                 # [NEW] Canonical DSL2 entry point
│   │   ├── nextflow.config         # Docker config, default params
│   │   └── configs/
│   │       ├── pyradiomics.yaml    # Radiomic extraction settings
│   │       ├── hyperparameters.yaml # Nested CV params (full dataset)
│   │       ├── hyperparameters_small.yaml # [NEW] Fast test params (12 subjects)
│   │       └── training.config     # [NEW] Training pipeline config overrides
│   ├── ftd_diagnosis/
│   │   ├── util/
│   │   │   ├── merge_radiomics.r   # Merge feature CSVs into feat_all.csv
│   │   │   ├── process_metrics.r   # Aggregate CV metrics
│   │   │   └── stability.r         # Feature frequency/stability analysis
│   │   ├── sequential/
│   │   │   ├── RFE.r               # RFE feature selection + sequential training
│   │   │   └── lasso.r             # LASSO feature selection + sequential training
│   │   └── parallel/
│   │       ├── features_selection.r # LASSO/RFE for parallel training
│   │       └── models/
│   │           ├── XGBoost.r       # XGBoost with nested CV + MLflow logging
│   │           ├── random_forest.r
│   │           ├── svm.r
│   │           └── kNN.r
│   ├── data/external/
│   │   └── ROI_labels.tsv          # 78 brain region labels (Index, Label)
│   ├── dockerfiles/
│   │   ├── freesurfer.dockerfile   # Builds clinical-freesurfer image
│   │   ├── fsl.dockerfile          # Builds clinical-fsl image
│   │   ├── pyradiomics.dockerfile  # Builds clinical-pyradiomics image
│   │   └── ftd-training.dockerfile # Builds ftd-training image
│   ├── docker-compose.yml          # Build-only compose for pipeline images
│   ├── dockerfile                  # nextflow_worker service Dockerfile
│   └── .env.example
│
├── docs/                           # MkDocs documentation
│   ├── docs/                       # Markdown source files
│   ├── mkdocs.yml
│   ├── TECHNICAL_REPORT.md
│   ├── CHANGES_AND_PERFORMANCE.md
│   └── REPORT_FINALE_COMPLETO.md
│
└── docker-compose.yml              # Main stack (7 services)
```

---

## Microservices Summary

| Service | Container name | Host port | Technology |
|---------|---------------|-----------|-----------|
| `api_gateway` | `clinical_api_gateway` | 127.0.0.1:8006 | FastAPI + SQLite + JWT |
| `orchestrator` | `clinical_orchestrator` | 127.0.0.1:8001 | FastAPI + SQLAlchemy |
| `model_service` | `clinical_model_service` | 127.0.0.1:8003 | FastAPI + MLflow |
| `llm_service` | `clinical_llm_service` | 127.0.0.1:8002 | FastAPI + Groq/Claude |
| `inference_engine` | `inference_engine` | 127.0.0.1:8004 | R + Plumber + uwot + xgboost |
| `frontend` | `clinical_frontend` | 5173 | React 18 + Vite + TailwindCSS |
| `nextflow_worker` | `nextflow_worker` | 127.0.0.1:8005 | FastAPI + Nextflow + DooD |

---

## Docker Volumes

| Volume | Mount point | Shared between |
|--------|------------|----------------|
| `clinical_twin_shared_data` | `/shared_data` | orchestrator, model_service, inference_engine, llm_service, nextflow_worker |
| `clinical_twin_db` | `/shared_db` | api_gateway, orchestrator |
| `/tmp/nextflow_work` (bind) | `/tmp/nextflow_work` | nextflow_worker ↔ host Docker daemon |
| `/var/run/docker.sock` (bind) | `/var/run/docker.sock` | nextflow_worker → host Docker daemon (DooD) |

---

## Key Files Added in Sessions 2026-05-27/28

| File | Type | Purpose |
|------|------|---------|
| `nextflow_worker/nextflow/main.nf` | New | Canonical DSL2 entry point for manual/CI Nextflow runs |
| `nextflow_worker/nextflow/configs/training.config` | New | Training pipeline parameter overrides (separate from code) |
| `nextflow_worker/nextflow/configs/hyperparameters_small.yaml` | New | Reduced nested CV params for 12-subject test datasets |

---

## Inter-Service Communication

```
Frontend ──HTTP──► API Gateway ──HTTP──► Orchestrator
                                             │
                              ┌──────────────┼──────────────┐
                              │              │              │
                       Model Service  Nextflow Worker   (polling)
                              │              │
                      Inference Engine  [Docker daemon]
                                            │
                                    [4 pipeline containers]
                                    clinical-freesurfer
                                    clinical-fsl
                                    clinical-pyradiomics
                                    ftd-training
```

Data exchange:
- REST APIs (HTTP/JSON): control flow and task coordination
- Shared Docker volume (`/shared_data`): large files (NIfTI, CSVs, models, results)
- Docker socket (`/var/run/docker.sock`): DooD — nextflow_worker spawns containers on host

---

## ROI_labels.tsv Format

The file `nextflow_worker/data/external/ROI_labels.tsv` defines the 78 brain regions:

```tsv
Index	Label
1	Left-Cerebral-White-Matter
2	Left-Cerebral-Cortex
...
78	Right-Cerebral-Cortex
```

This file is:
1. Copied to `/shared_data/ROI_labels.tsv` at `nextflow_worker` startup
2. Used by `roi_creator` process (fslmaths) to create binary masks
3. Used by `merge_radiomics.r` to build feature CSV filenames
4. Used by `inference_logic.R` for ROI→feature column mapping
5. Must be parsed with `header=TRUE, sep="\t"` (not `header=FALSE, sep=""`)
