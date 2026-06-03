# Installazione — Clinical Twin

---

## Requisiti di sistema

| Componente | Minimo | Raccomandato |
|-----------|--------|-------------|
| OS | Windows 10 (WSL2), macOS 12, Ubuntu 20.04 | Ubuntu 22.04 LTS |
| CPU | 4 core | 16+ core (FreeSurfer è multi-threaded) |
| RAM | 16 GB | 32+ GB |
| Disco | 50 GB liberi | 200+ GB (FreeSurfer: ~5 GB/soggetto) |
| Docker | 24.x | Ultima versione |
| Docker Compose | 2.x | Ultima versione |
| NVIDIA GPU | — | RTX 3080+ / A100 (per FastSurfer) |

---

## Step 1 — Installa Docker

### Windows
1. Scarica Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Abilita l'integrazione WSL2 durante la configurazione
3. Alloca almeno 16 GB RAM in Docker Desktop → Settings → Resources

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

## Step 2 — Clona il repository

```bash
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD
```

---

## Step 3 — Ottieni la licenza FreeSurfer

La licenza FreeSurfer è **obbligatoria** per il funzionamento della pipeline.

1. Registrati su: https://surfer.nmr.mgh.harvard.edu/registration.html
2. Riceverai un file `license.txt` per email
3. Copialo nel progetto:

```bash
cp /path/to/license.txt nextflow_worker/license.txt
```

> Senza questo file, FreeSurfer si interrompe immediatamente con `ERROR: License file not found`.

---

## Step 4 — Configura i file di ambiente

```bash
for svc in api_gateway orchestrator model_service llm_service; do
    cp ${svc}/.env.example ${svc}/.env
done
```

**Minimo richiesto:** imposta `SECRET_KEY` con lo stesso valore in
`api_gateway/.env` e `orchestrator/.env`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Vedi [Configurazione](Configurazione.it.md) per il riferimento completo alle variabili.

---

## Step 5 — Costruisci le immagini Docker Nextflow

```bash
docker compose -f nextflow_worker/docker-compose.yml build
```

Output atteso (ogni immagine ~2–5 GB, totale ~15 GB):
```
[+] Building clinical-freesurfer  ... done
[+] Building clinical-fsl         ... done
[+] Building clinical-pyradiomics ... done
[+] Building ftd-training         ... done
```

> Questo step può richiedere 20–40 minuti al primo build.

---

## Step 6 — Avvia il sistema

```bash
docker compose up --build -d
```

Verifica che i 7 servizi siano in esecuzione:
```bash
docker compose ps
# Atteso: 7 container con stato "Up"
```

---

## Step 7 — Verifica l'installazione

```bash
# Controlla tutti gli health endpoint
for port in 8006 8001 8003 8005; do
    echo -n "Porta $port: "
    curl -s http://localhost:$port/health
    echo
done

# Apri la dashboard
# Vai su http://localhost:5173 nel browser
```

---

## Step 8 — Registra il primo utente

```bash
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test123"}'
```

Per il test rapido della pipeline, imposta `TEST_MODE=true` in `orchestrator/.env`,
poi riavvia: `docker compose restart orchestrator`.

Vedi [Guida Rapida](Guida_Rapida.it.md) per il walkthrough della prima analisi.

---

## Setup GPU NVIDIA (opzionale)

```bash
# Installa NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verifica
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

## Disinstallazione

```bash
docker compose down -v
docker rmi clinical-freesurfer clinical-fsl clinical-pyradiomics ftd-training
cd .. && rm -rf Tesi-FTD
```
