# Configuration — Clinical Twin

The platform is configured via `.env` files, one per service.
These files must be set up before starting the system.

---

## Configuration Files

```
Tesi-FTD/
├── api_gateway/.env
├── orchestrator/.env
├── model_service/.env
├── llm_service/.env
└── nextflow_worker/.env  (optional — variables injected via docker-compose.yml)
```

Copy the example files to get started:
```bash
cp api_gateway/.env.example    api_gateway/.env
cp orchestrator/.env.example   orchestrator/.env
cp model_service/.env.example  model_service/.env
cp llm_service/.env.example    llm_service/.env
```

---

## 1. api_gateway/.env

```env
SECRET_KEY=change-this-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Shared JWT signing key — must match `orchestrator/.env` |
| `ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token TTL in minutes (default: 30) |

---

## 2. orchestrator/.env

```env
SECRET_KEY=change-this-to-a-long-random-string
ALGORITHM=HS256
DATABASE_URL=sqlite:////shared_db/clinical_twin.db

MODEL_SERVICE_URL=http://model_service:8000
NEXTFLOW_WORKER_URL=http://nextflow_worker:8000
AUTH_SERVICE_URL=http://api_gateway:8000

SHARED_VOLUME_DIR=/shared_data

USE_MOCK=false
TEST_MODE=false
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Must match `api_gateway/.env` |
| `DATABASE_URL` | No | SQLite path (default: shared volume) |
| `MODEL_SERVICE_URL` | No | Internal Docker network URL |
| `NEXTFLOW_WORKER_URL` | No | Internal Docker network URL |
| `SHARED_VOLUME_DIR` | No | Path of shared volume inside container |
| `USE_MOCK` | No | `true` = use MockRunner (no Nextflow, synthetic CSV) |
| `TEST_MODE` | No | `true` = activate `mock_freesurfer` in Nextflow (30s instead of 6–8h) |

### USE_MOCK vs TEST_MODE

| Flag | What it does | When to use |
|------|-------------|-------------|
| `USE_MOCK=true` | Skips Nextflow entirely, generates a synthetic feature CSV | Unit testing orchestrator logic |
| `TEST_MODE=true` | Runs real Nextflow but replaces FreeSurfer with a synthetic mock (concentric spheres) | Integration testing the full pipeline quickly |
| Both `false` | Full production pipeline with FreeSurfer | Production use |

---

## 3. model_service/.env

```env
MLFLOW_TRACKING_URI=https://dagshub.com/your-username/Tesi-FTD.mlflow
MLFLOW_TRACKING_USERNAME=your-dagshub-username
MLFLOW_TRACKING_PASSWORD=your-dagshub-token

R_ENGINE_URL=http://inference_engine:8000/infer
SHARED_VOLUME_DIR=/shared_data
```

| Variable | Required | Description |
|----------|----------|-------------|
| `MLFLOW_TRACKING_URI` | No | DagsHub MLflow endpoint. If absent, fallback to local model |
| `MLFLOW_TRACKING_USERNAME` | No | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | No | DagsHub token (from DagsHub → Settings → Tokens) |
| `R_ENGINE_URL` | No | Plumber endpoint for inference (default: internal Docker URL) |
| `SHARED_VOLUME_DIR` | No | Path of shared volume |

**Model fallback chain** (when MLflow is unavailable):
1. `/shared_data/models/{model_name}/model.rds`
2. `/app/model.rds` (bind-mounted from `model_service/model.rds`)
3. `/shared_data/models/model.rds`

---

## 4. llm_service/.env

```env
SECRET_KEY=change-this-to-a-long-random-string
GROQ_API_KEY=gsk_...
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | For JWT validation |
| `GROQ_API_KEY` | No | Groq API key for the LLM assistant (or use `ANTHROPIC_API_KEY` for Claude) |

---

## 5. Nextflow Pipeline Variables (docker-compose.yml)

These variables are injected into the `nextflow_worker` container via `docker-compose.yml`:

```yaml
environment:
  - SHARED_VOLUME_DIR=/shared_data
  - HOST_SHARED_VOLUME_DIR=${HOST_SHARED_VOLUME_DIR:-/shared_data}
  - NF_OUTDIR=${NF_OUTDIR:-/shared_data/nf_output}
  - NF_LABELS=${NF_LABELS:-/app/data/external/ROI_labels.tsv}
  - NF_SETTINGS=${NF_SETTINGS:-/app/nextflow/configs/pyradiomics.yaml}
  - MIG_DEVICE=${MIG_DEVICE:-all}
```

| Variable | Description |
|----------|-------------|
| `SHARED_VOLUME_DIR` | Shared volume path inside the container |
| `HOST_SHARED_VOLUME_DIR` | Shared volume path on the **host** (DooD — must be a host path) |
| `NF_OUTDIR` | Nextflow pipeline output directory |
| `NF_LABELS` | Path to `ROI_labels.tsv` (78 brain region labels) |
| `NF_SETTINGS` | Path to `pyradiomics.yaml` (radiomic extraction parameters) |
| `MIG_DEVICE` | NVIDIA MIG instance UUID for FastSurfer GPU (e.g., `MIG-GPU-xxxxxxxx-...`). Leave as `all` for standard GPUs |

---

## 6. GPU Configuration

### Standard NVIDIA GPU
No extra configuration needed. FastSurfer uses all available GPUs by default (`MIG_DEVICE=all`).

### NVIDIA MIG (Multi-Instance GPU)
For HPC systems with GPU partitioning:
```bash
# Find your MIG instance UUID
nvidia-smi -L

# Set in docker-compose.yml or .env:
MIG_DEVICE=MIG-GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### CPU-only mode
```yaml
# In docker-compose.yml
environment:
  - MIG_DEVICE=           # empty = no GPU
```
Or use `brain_segmenter=freesurfer` (CPU-based, no GPU required).

---

## 7. FreeSurfer License

The FreeSurfer license file must be present at:
```
nextflow_worker/license.txt
```

Register free at: https://surfer.nmr.mgh.harvard.edu/registration.html

The file is automatically copied to `/tmp/nextflow_work/license.txt` at
`nextflow_worker` startup (via the lifespan hook in `main.py`), which is the
path referenced by `nextflow.config` for DooD bind-mounts.

---

## 8. Environment Validation

Before starting, verify key settings:
```bash
# Check SECRET_KEY matches across services
grep SECRET_KEY api_gateway/.env orchestrator/.env

# Check MLflow connectivity (optional)
curl -s "$MLFLOW_TRACKING_URI/api/2.0/mlflow/experiments/list" \
  -u "$MLFLOW_TRACKING_USERNAME:$MLFLOW_TRACKING_PASSWORD"

# Check Docker socket for DooD
ls -la /var/run/docker.sock
```
