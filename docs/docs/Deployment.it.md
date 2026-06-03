# Guida al Deployment — Clinical Twin

---

## Prerequisiti

| Componente | Versione | Note |
|-----------|---------|------|
| Docker Desktop | ≥ 4.x | Abilitare "Use WSL 2 based engine" su Windows |
| Docker Compose | ≥ 2.x | Incluso in Docker Desktop |
| RAM | ≥ 16 GB | FreeSurfer richiede ~8–12 GB per processo |
| Disco | ≥ 100 GB | Output FreeSurfer: ~5 GB per soggetto |
| NVIDIA GPU | Opzionale | Richiesto solo per FastSurfer (modalità CUDA) |
| Licenza FreeSurfer | **Richiesta** | Registrazione gratuita su surfer.nmr.mgh.harvard.edu |

---

## Step 1 — Clone e configurazione

```bash
git clone https://github.com/carlosto033/Tesi-FTD.git
cd Tesi-FTD

# Copia i file di ambiente
cp api_gateway/.env.example    api_gateway/.env
cp orchestrator/.env.example   orchestrator/.env
cp model_service/.env.example  model_service/.env
cp llm_service/.env.example    llm_service/.env
```

Posiziona la licenza FreeSurfer:
```bash
cp /path/to/your/license.txt nextflow_worker/license.txt
```

---

## Step 2 — Build immagini Docker Nextflow

La pipeline neuroimaging richiede 4 immagini Docker specializzate.
Costruiscile **prima** di avviare lo stack principale:

```bash
docker compose -f nextflow_worker/docker-compose.yml build
```

Questo costruisce:
- `clinical-freesurfer` — FreeSurfer 7.4 + nibabel + Python
- `clinical-fsl` — FSL (fslmaths per maschere ROI)
- `clinical-pyradiomics` — PyRadiomics + Python
- `ftd-training` — R + mlr + xgboost + mlflow (pipeline di training)

> **Importante:** i nomi delle immagini devono corrispondere esattamente
> (`clinical-freesurfer`, non `freesurfer`).

---

## Step 3 — Avvio dello stack principale

```bash
docker compose up --build -d
```

Verifica che tutti i servizi siano attivi:
```bash
docker compose ps

curl http://localhost:8006/health  # api_gateway
curl http://localhost:8001/health  # orchestrator
curl http://localhost:8003/health  # model_service
curl http://localhost:8004/health  # inference_engine
curl http://localhost:8005/health  # nextflow_worker
```

---

## Step 4 — Registra il primo utente

```bash
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tuapassword"}'
```

---

## URL dei servizi

| Servizio | URL |
|---------|-----|
| Dashboard frontend | http://localhost:5173 |
| API Gateway Swagger | http://localhost:8006/docs |
| Orchestrator Swagger | http://localhost:8001/docs |
| Model Service Swagger | http://localhost:8003/docs |
| Nextflow Worker Swagger | http://localhost:8005/docs |

---

## DooD (Docker-out-of-Docker)

Il `nextflow_worker` avvia i container della pipeline connettendosi al
**daemon Docker dell'host** tramite mount del socket:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - /tmp/nextflow_work:/tmp/nextflow_work
```

Il path `/tmp/nextflow_work` è un bind-mount host↔container usato come
punto di coordinamento per la licenza FreeSurfer e la work directory di Nextflow.

---

## Risoluzione problemi

### Immagini Docker non trovate: `clinical-freesurfer`

La pipeline Nextflow richiede immagini nominate `clinical-freesurfer`, `clinical-fsl`,
`clinical-pyradiomics`. Se Nextflow riporta "image not found":
```bash
docker compose -f nextflow_worker/docker-compose.yml build
docker images | grep clinical
```

### Errore licenza FreeSurfer

Sintomo: `ERROR: License file not found`

1. Verifica che il file esista: `ls nextflow_worker/license.txt`
2. Riavvia il container: `docker compose restart nextflow_worker`
3. Verifica la copia: `docker exec nextflow_worker ls /tmp/nextflow_work/license.txt`

### Pipeline bloccata dopo FreeSurfer

Controlla i log Nextflow:
```bash
docker exec nextflow_worker cat /tmp/nextflow_work/cache_*/nextflow.log | tail -50
```

### Inferenza restituisce "Sconosciuto"

Il file modello è mancante o corrotto:
```bash
docker exec model_service ls -la /app/model.rds
# Deve essere > 1000 byte. Un modello XGBoost esteso valido è ~50KB+
```

---

## Checklist produzione

- [ ] Cambia tutte le `SECRET_KEY` con stringhe casuali lunghe (`openssl rand -hex 32`)
- [ ] Configura HTTPS tramite reverse proxy (nginx/caddy)
- [ ] Imposta la rotazione dei log Docker
- [ ] Configura backup del volume `clinical_twin_db`
- [ ] Configura MLflow con un modello reale e assegna l'alias `@champion`
- [ ] Testa con `TEST_MODE=true` prima di eseguire job FreeSurfer reali
