# Deployment Guide — MLOps

---

## Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| Docker Desktop | ≥ 4.x | Enable "Use WSL 2 based engine" on Windows |
| Docker Compose | ≥ 2.x | Included in Docker Desktop |
| RAM | ≥ 16 GB | FreeSurfer requires ~8–12 GB per process |
| Disk | ≥ 100 GB | FreeSurfer output: ~5 GB per subject |
| NVIDIA GPU | Optional | Required only for FastSurfer (CUDA mode) |
| NVIDIA Container Toolkit | If GPU | `apt install nvidia-container-toolkit` |
| FreeSurfer license | **Required** | Register at surfer.nmr.mgh.harvard.edu |

---

## Step 1 — Clone and configure

```bash
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD

# Copy environment files
cp api_gateway/.env.example    api_gateway/.env
cp orchestrator/.env.example   orchestrator/.env
cp model_service/.env.example  model_service/.env
cp llm_service/.env.example    llm_service/.env

# Set your SECRET_KEY (must be the same in api_gateway and orchestrator)
# Edit each .env with your values
```

Place the FreeSurfer license:
```bash
cp /path/to/your/license.txt nextflow_worker/license.txt
```

---

## Step 2 — Build Nextflow Docker images

The neuroimaging pipeline requires 4 specialized Docker images.
Build them **before** starting the main stack:

```bash
# Build all 4 pipeline images at once
docker compose -f nextflow_worker/docker-compose.yml build
```

This builds:
- `clinical-freesurfer` — FreeSurfer 7.4 + nibabel + Python
- `clinical-fsl` — FSL (fslmaths for ROI masks)
- `clinical-pyradiomics` — PyRadiomics + Python
- `ftd-training` — R + mlr + xgboost + mlflow (for training pipeline)

> **Important:** image names must match exactly (`clinical-freesurfer`, not `freesurfer`).
> The `docker-compose.yml` in `nextflow_worker/` uses the correct names.

---

## Step 3 — Start the main stack

```bash
docker compose up --build -d
```

Wait for all services to be healthy:
```bash
docker compose ps

# Check health endpoints
curl http://localhost:8006/health  # api_gateway
curl http://localhost:8001/health  # orchestrator
curl http://localhost:8003/health  # model_service
curl http://localhost:8004/health  # inference_engine
curl http://localhost:8005/health  # nextflow_worker
```

---

## Step 4 — Register first user

```bash
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

---

## Service URLs

| Service | URL |
|---------|-----|
| Frontend dashboard | http://localhost:5173 |
| API Gateway Swagger | http://localhost:8006/docs |
| Orchestrator Swagger | http://localhost:8001/docs |
| Model Service Swagger | http://localhost:8003/docs |
| Nextflow Worker Swagger | http://localhost:8005/docs |

---

## DooD (Docker-out-of-Docker) Setup

The `nextflow_worker` spawns Nextflow sub-containers by connecting to the
**host Docker daemon** via socket mount:

```yaml
# docker-compose.yml (nextflow_worker section)
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - /tmp/nextflow_work:/tmp/nextflow_work
```

The directory `/tmp/nextflow_work` is a **host↔container bind-mount** used as
coordination point. It must exist on the host before Docker starts:

```bash
# On Linux/macOS:
mkdir -p /tmp/nextflow_work

# On Windows (Docker Desktop + WSL2):
# Docker Desktop creates this automatically via the bind-mount
```

**Why this matters:** In DooD, all `-v` bind-mounts in Nextflow processes are
interpreted by the HOST Docker daemon. The path `/tmp/nextflow_work/license.txt`
must exist on the host — not just inside the container.

---

## GPU Deployment

### NVIDIA GPU (standard)
```bash
# Verify GPU visibility
nvidia-smi

# The pipeline will use GPU automatically when brain_segmenter=fastsurfer
# No extra configuration needed (MIG_DEVICE defaults to "all")
```

### NVIDIA MIG (Multi-Instance GPU)
```bash
# List MIG instances
nvidia-smi -L

# Set in your environment:
export MIG_DEVICE="MIG-GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

---

## Stopping the Stack

```bash
# Stop without removing volumes (data preserved)
docker compose down

# Stop and remove all data (WARNING: irreversible)
docker compose down -v
```

---

## Troubleshooting

### Port 8000 already in use

If another service occupies port 8000 on your host, the `api_gateway` binding on
`127.0.0.1:8006` → internal port `8000` should not conflict (the host port is 8006).
If you see conflicts, check:
```bash
netstat -an | grep 8006
# or on Windows:
netstat -an | findstr 8006
```

### Docker images not found: `clinical-freesurfer`

The Nextflow pipeline requires images named `clinical-freesurfer`, `clinical-fsl`,
`clinical-pyradiomics`. If Nextflow reports "image not found":
```bash
# Rebuild pipeline images
docker compose -f nextflow_worker/docker-compose.yml build

# Verify images exist
docker images | grep clinical
```

### FreeSurfer license error

Symptom: `ERROR: License file not found`

1. Verify the license file exists: `ls nextflow_worker/license.txt`
2. Verify the nextflow_worker container copied it: 
   ```bash
   docker exec nextflow_worker ls /tmp/nextflow_work/license.txt
   ```
3. If missing, restart the container: `docker compose restart nextflow_worker`

### Pipeline stuck after FreeSurfer

If Nextflow completes but no `radiomics_features.csv` appears:
```bash
# Check Nextflow logs
docker exec nextflow_worker cat /tmp/nextflow_work/cache_*/nextflow.log | tail -50

# Check if ROI masks were generated
ls /tmp/nextflow_work/cache_*/work/*/ROI/ | head -20
```

### Inference returns "Sconosciuto" with NA confidence

The model file is missing or corrupt. Check:
```bash
docker exec model_service ls -la /app/model.rds
# Should be > 1000 bytes. A valid XGBoost extended model is ~50KB+
```

---

## Production Hardening Checklist

- [ ] Change all `SECRET_KEY` values to long random strings (`openssl rand -hex 32`)
- [ ] Configure HTTPS via reverse proxy (nginx/caddy) with valid TLS certificate
- [ ] Restrict Docker socket access (read-only, dedicated group)
- [ ] Enable Docker log rotation
- [ ] Set up backup for `clinical_twin_db` volume (SQLite database)
- [ ] Configure MLflow with a real model and assign `@champion` alias
- [ ] Test with `TEST_MODE=true` before running real FreeSurfer jobs
