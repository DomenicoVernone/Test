# Installation — MLOps

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 (WSL2), macOS 12, Ubuntu 20.04 | Ubuntu 22.04 LTS |
| CPU | 4 cores | 16+ cores (FreeSurfer is multi-threaded) |
| RAM | 16 GB | 32+ GB |
| Disk | 50 GB free | 200+ GB (FreeSurfer: ~5 GB/subject) |
| Docker | 24.x | Latest |
| Docker Compose | 2.x | Latest |
| NVIDIA GPU | — | RTX 3080+ / A100 (for FastSurfer) |

---

## Step 1 — Install Docker

### Windows
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Enable WSL2 integration during setup
3. Allocate at least 16 GB RAM in Docker Desktop → Settings → Resources

### macOS
```bash
brew install --cask docker
```

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 2 — Clone the repository

```bash
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
```

---

## Step 3 — Get the FreeSurfer license

The FreeSurfer license is **required** for the neuroimaging pipeline to work.

1. Register at: https://surfer.nmr.mgh.harvard.edu/registration.html
2. You will receive a `license.txt` file by email
3. Copy it to the project:

```bash
cp /path/to/license.txt nextflow_worker/license.txt
```

> Without this file, FreeSurfer will crash immediately with `ERROR: License file not found`.

---

## Step 4 — Configure environment files

```bash
# Copy all example files
for svc in api_gateway orchestrator model_service llm_service; do
    cp ${svc}/.env.example ${svc}/.env
done
```

Edit each `.env` file:

**Minimum required:** set `SECRET_KEY` to the same value in both `api_gateway/.env` and `orchestrator/.env`:
```bash
# Generate a secure key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output into SECRET_KEY in both files
```

See [Configuration](Configurazione.md) for the full variable reference.

---

## Step 5 — Build Nextflow pipeline images

```bash
docker compose -f nextflow_worker/docker-compose.yml build
```

Expected output (each image ~2–5 GB, total ~15 GB):
```
[+] Building clinical-freesurfer ... done
[+] Building clinical-fsl        ... done
[+] Building clinical-pyradiomics ... done
[+] Building ftd-training        ... done
```

> This step may take 20–40 minutes on first build (downloading base images).

---

## Step 6 — Start the system

```bash
docker compose up --build -d
```

Verify all 7 services are running:
```bash
docker compose ps

# Expected: 7 containers with status "Up"
# clinical_api_gateway
# clinical_orchestrator
# clinical_model_service
# clinical_llm_service
# inference_engine
# clinical_frontend
# nextflow_worker
```

---

## Step 7 — Verify installation

```bash
# Check all health endpoints
for port in 8006 8001 8003 8005; do
    echo -n "Port $port: "
    curl -s http://localhost:$port/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'))"
done

# Open the dashboard
open http://localhost:5173   # macOS
# or xdg-open http://localhost:5173  (Linux)
# or navigate to http://localhost:5173 in your browser (Windows)
```

---

## Step 8 — Register first user and test

```bash
# Register
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test123"}'

# For quick pipeline test, set TEST_MODE=true in orchestrator/.env
# Then restart: docker compose restart orchestrator
```

See [Quickstart](Guida_Rapida.md) for the first analysis walkthrough.

---

## NVIDIA GPU Setup (optional)

For FastSurfer acceleration:

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

## Uninstall

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Remove pipeline images
docker rmi clinical-freesurfer clinical-fsl clinical-pyradiomics ftd-training

# Remove project
cd .. && rm -rf Tesi-FTD
```
