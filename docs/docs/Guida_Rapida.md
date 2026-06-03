# Quickstart — MLOps

This guide covers the fastest path to run your first MRI analysis.

---

## Estimated Times

| Mode | Total time | Use case |
|------|-----------|---------|
| **TEST_MODE=true** (mock FreeSurfer) | ~5–15 minutes | Development, testing pipeline |
| **FreeSurfer CPU** (real segmentation) | ~4–10 hours | Production, research |
| **FastSurfer GPU** (CUDA) | ~30–60 minutes | Production with NVIDIA GPU |

---

## Prerequisites

1. Docker Desktop running
2. All `.env` files configured (see [Configuration](Configurazione.md))
3. FreeSurfer license at `nextflow_worker/license.txt`
4. Pipeline Docker images built: `docker compose -f nextflow_worker/docker-compose.yml build`

---

## Quickstart: Test Mode (recommended for first run)

### Step 1 — Set TEST_MODE

Edit `orchestrator/.env`:
```env
TEST_MODE=true
USE_MOCK=false
```

This activates `mock_freesurfer`: instead of running FreeSurfer `recon-all` (6–8 hours),
the pipeline generates synthetic brain masks in ~30 seconds.

### Step 2 — Start the system

```bash
docker compose up --build -d
```

Wait ~30 seconds for all services to become ready.

### Step 3 — Register and login

```bash
# Register
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"test123"}'

# Login and save token
TOKEN=$(curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"test123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

Or use the browser: open **http://localhost:5173** and log in directly.

### Step 4 — Upload an MRI

Via browser (recommended):
1. Open http://localhost:5173
2. Click **"Carica MRI"** or **"New Analysis"**
3. Select a `.nii` or `.nii.gz` file
4. Choose model `HC_vs_bvFTD`
5. Click **"Analizza"**

Via curl:
```bash
curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/scan.nii.gz" \
  -F "model_name=HC_vs_bvFTD"
```

Response:
```json
{"task_id": 1, "status": "PENDING"}
```

### Step 5 — Wait for results

The frontend **automatically polls** the task status every 3 seconds.
You will see the task card change from **IN ELABORAZIONE** → **COMPLETATO**.

Total time with `TEST_MODE=true`: approximately **5–15 minutes**.

To monitor via API:
```bash
# Poll status
curl http://localhost:8001/analyze/status/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Step 6 — View results

When completed, click the task card in the sidebar to see:
- **Diagnosis**: `HC` (Healthy Control) or `bvFTD`
- **Confidence**: e.g., 79.57%
- **3D UMAP**: interactive visualization showing the patient's position relative to the training cohort

---

## Complete Workflow Diagram

```
[Docker Desktop running]
        │
        ▼
docker compose up --build -d
        │
        ▼
http://localhost:5173  ──► Login
        │
        ▼
Upload scan.nii.gz  ──► Select model: HC_vs_bvFTD
        │
        ▼
Orchestrator creates task (PENDING)
        │
        ▼
Phase 0: model_service → brain_segmenter = "freesurfer"
        │
        ▼
Phase 1: Nextflow pipeline
  ├─ TEST_MODE=true  → mock_freesurfer (30s) → ROI → radiomics → CSV
  └─ TEST_MODE=false → FreeSurfer recon-all (6–8h) → ROI → radiomics → CSV
        │
        ▼
Phase 2: model_service → inference_engine (R)
  ├─ XGBoost prediction: HC or bvFTD
  ├─ Confidence: 0.00–1.00
  └─ UMAP 3D: historical space + new patient
        │
        ▼
Task → COMPLETED (100%)
        │
        ▼
Frontend shows: diagnosis + confidence + 3D visualization
```

---

## Production Mode (real FreeSurfer)

To analyze real MRI data:

1. Set `TEST_MODE=false` in `orchestrator/.env`
2. Upload a real T1 MRI scan (`.nii` or `.nii.gz`)
3. The pipeline will run full FreeSurfer `recon-all` (~4–10 hours on CPU)
4. The task card shows a live timer during processing
5. Results appear automatically when completed

> **Tip:** Use FastSurfer with a GPU to reduce segmentation time from ~8h to ~30min.
> Set `MIG_DEVICE=all` (or your MIG UUID) and the orchestrator will request `brain_segmenter=fastsurfer`
> when the deployed model was trained with FastSurfer.

---

## Stopping

```bash
# Stop without losing data
docker compose down

# Stop and delete all volumes (WARNING: all task history deleted)
docker compose down -v
```
