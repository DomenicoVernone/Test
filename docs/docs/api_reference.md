# API Reference — MLOps

The MLOps platform exposes REST APIs across 5 microservices.
All services communicate over the Docker network `mlops_net`.
External access is bound to `127.0.0.1` (loopback only).

---

## Service Ports

| Service | Container port | Host port (external) | Swagger UI |
|---------|---------------|----------------------|------------|
| api_gateway | 8000 | `127.0.0.1:8006` | http://localhost:8006/docs |
| orchestrator | 8000 | `127.0.0.1:8001` | http://localhost:8001/docs |
| model_service | 8000 | `127.0.0.1:8003` | http://localhost:8003/docs |
| llm_service | 8000 | `127.0.0.1:8002` | http://localhost:8002/docs |
| inference_engine (R/Plumber) | 8000 | `127.0.0.1:8004` | — |
| nextflow_worker | 8000 | `127.0.0.1:8005` | http://localhost:8005/docs |

---

## Authentication

All endpoints (except `/signup`, `/login`, `/health`) require a JWT Bearer token.

### Obtain a Token

```bash
curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```
Authorization: Bearer <access_token>
```

JWT tokens are signed with `HS256` using the `SECRET_KEY` shared between
`api_gateway` and `orchestrator`. Default expiry: 30 minutes.

---

## 1. API Gateway — port 8006

### POST /signup
Register a new user.

```bash
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"securepass"}'
```

Response `200`:
```json
{"message": "User created successfully"}
```

### POST /login
Authenticate and receive a JWT token.

```bash
curl -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"securepass"}'
```

Response `200`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET /me
Return information about the authenticated user.

```bash
curl http://localhost:8006/me \
  -H "Authorization: Bearer <token>"
```

Response `200`:
```json
{"username": "doctor01"}
```

### GET /health
Service liveness check.
```json
{"status": "ok", "service": "api_gateway"}
```

---

## 2. Orchestrator — port 8001

### POST /analyze/upload
Upload a NIfTI file and start the full diagnostic pipeline.

```bash
curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/scan.nii.gz" \
  -F "model_name=HC_vs_bvFTD"
```

Response `202`:
```json
{
  "task_id": 17,
  "status": "PENDING",
  "filename": "a3f8b21c_scan.nii.gz",
  "model_name": "HC_vs_bvFTD"
}
```

> **Note:** The filename is prefixed with an 8-character MD5 hash to avoid collisions.

### GET /analyze/status/{task_id}
Poll the status and retrieve results when completed.

```bash
curl http://localhost:8001/analyze/status/17 \
  -H "Authorization: Bearer <token>"
```

Response while running:
```json
{
  "task_id": 17,
  "status": "PROCESSING",
  "progress": 10.0,
  "filename": "a3f8b21c_scan.nii.gz"
}
```

Response when completed (`status = "COMPLETED"`):
```json
{
  "task_id": 17,
  "status": "COMPLETED",
  "progress": 100.0,
  "filename": "a3f8b21c_scan.nii.gz",
  "model_name": "HC_vs_bvFTD",
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [
      {"x": -1.23, "y": 0.45, "z": 2.11, "label": "HC", "subject_id": "Paziente_Storico_1"},
      {"x":  1.87, "y": -0.32, "z": -1.05, "label": "bvFTD", "subject_id": "Paziente_Storico_2"}
    ],
    "nuovo_paziente": {
      "x": -0.91, "y": 0.38, "z": 1.74
    }
  }
}
```

**Task status values:**

| Status | Meaning |
|--------|---------|
| `PENDING` | Task created, pipeline not started yet |
| `PROCESSING` | Nextflow pipeline running (feature extraction) |
| `ANALYZING_R` | R inference engine running |
| `COMPLETED` | Diagnosis ready |
| `ERROR` | Pipeline failed |

### GET /analyze/tasks
List all tasks for the authenticated user.

```bash
curl http://localhost:8001/analyze/tasks \
  -H "Authorization: Bearer <token>"
```

Response:
```json
[
  {
    "id": 17,
    "filename": "a3f8b21c_sub-01_ses-test_T1w.nii",
    "status": "COMPLETED",
    "model_name": "HC_vs_bvFTD",
    "created_at": "2026-05-28T14:30:00",
    "updated_at": "2026-05-28T18:51:22",
    "progress": 100.0
  }
]
```

### GET /analyze/nifti/{task_id}/volume.nii.gz
Download the NIfTI file associated with a task (used by the 3D viewer).

### GET /health
```json
{"status": "ok", "service": "orchestrator"}
```

---

## 3. Model Service — port 8003

### POST /infer
Download the champion model from MLflow and trigger R inference.

```bash
curl -X POST http://localhost:8003/infer \
  -H "Content-Type: application/json" \
  -d '{"task_id": 17, "model_name": "HC_vs_bvFTD"}'
```

Response `200`:
```json
{
  "status": "ok",
  "result": {
    "status": "success",
    "task_id": "17",
    "diagnosi_predetta": "HC",
    "confidenza": 0.7957,
    "plot_data": { "storico": [...], "nuovo_paziente": {...} }
  }
}
```

MLflow fallback chain (in order if MLflow/DagsHub is unavailable):
1. `/shared_data/models/{model_name}/model.rds`
2. `/app/model.rds`
3. `/shared_data/models/model.rds`

### GET /model_info/{model_name}
Retrieve champion model metadata (called by orchestrator before preprocessing
to determine which brain segmenter was used during training).

```bash
curl http://localhost:8003/model_info/HC_vs_bvFTD
```

Response `200`:
```json
{
  "model_name": "HC_vs_bvFTD",
  "brain_segmenter": "freesurfer",
  "run_id": "abc123def456",
  "tags": {"model": "XGBoost", "brain_segmenter": "freesurfer"}
}
```

### GET /health
```json
{"status": "ok", "service": "model_service"}
```

---

## 4. Inference Engine (R/Plumber) — port 8004

The inference engine is an R Plumber server. It is called **only by model_service**,
never directly by the user.

### GET /health
```json
{"status": "ok"}
```

### POST /infer
Execute clinical inference and compute 3D UMAP embedding.

Parameters (JSON body):
- `task_id` — task identifier
- `model_name` — model name (for logging)
- `model_dir` — absolute path to the `.rds` model file

Response:
```json
{
  "status": "success",
  "task_id": "17",
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [
      {
        "x": -1.23, "y": 0.45, "z": 2.11,
        "label": "HC",
        "subject_id": "Paziente_Storico_1",
        "feature1": 0.432, "feature2": 1.87, "..."
      }
    ],
    "nuovo_paziente": {
      "x": -0.91, "y": 0.38, "z": 1.74,
      "feature1": 0.411, "feature2": 1.72, "..."
    }
  }
}
```

The `plot_data` object contains:
- `storico`: historical training patients with 3D UMAP coordinates + all radiomic features
- `nuovo_paziente`: new patient projected into the historical UMAP space

---

## 5. Nextflow Worker — port 8005

This service is called **only by the orchestrator**, not directly by the user.

### POST /start_preprocessing
Start the Nextflow preprocessing pipeline for a NIfTI file.

```json
{
  "task_id": "17",
  "input_path": "/shared_data/nifti/a3f8b21c_scan.nii.gz",
  "outdir": "/shared_data/temp_nf_17",
  "brain_segmenter": "freesurfer",
  "test_mode": false
}
```

Response `200`:
```json
{"status": "accepted", "message": "Nextflow avviato per il task 17"}
```

`test_mode: true` activates `mock_freesurfer` (bypasses FreeSurfer recon-all,
completes in ~30 seconds instead of 6–8 hours).

### GET /status/{task_id}
Poll Nextflow pipeline status.

```json
{"task_id": "17", "status": "RUNNING"}
```

Status values: `RUNNING`, `SUCCESS`, `FAILED`.

### GET /health
```json
{"status": "ok", "service": "nextflow_worker"}
```

---

## 6. LLM Service — port 8002

### POST /chat
Ask the AI assistant for clinical interpretation.

```bash
curl -X POST http://localhost:8002/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain this patient diagnosis",
    "context": {
      "diagnosi_predetta": "HC",
      "confidenza": 0.7957,
      "model_name": "HC_vs_bvFTD"
    }
  }'
```

Response `200`:
```json
{"response": "The patient has been classified as Healthy Control (HC) with 79.57% confidence..."}
```

### GET /health
```json
{"status": "ok", "service": "llm_service"}
```

---

## Error Handling

All services return standard HTTP status codes:

| Code | Meaning |
|------|---------|
| `200` | Success |
| `202` | Accepted (async task started) |
| `401` | Unauthorized (missing or invalid JWT) |
| `404` | Resource not found |
| `422` | Validation error (invalid request body) |
| `500` | Internal server error |

Error response format:
```json
{"detail": "Error description"}
```

---

## Data Contract: radiomics_features.csv

The central data artifact exchanged between `nextflow_worker` and `inference_engine`:

- Generated by: `feature_extraction` process in `preprocessing.nf`
- Location: `/shared_data/features/features_{task_id}.csv`
- Format: CSV with one row per subject, ~6,864 columns
- Column naming: `{ROI_name}_{pyradiomics_feature}` (e.g., `Hippocampus_original_shape_Volume`)
- ROI names sourced from: `ROI_labels.tsv` (78 brain regions)
