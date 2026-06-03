# Configurazione — Clinical Twin

La piattaforma è configurata tramite file `.env`, uno per servizio.
Questi file devono essere configurati prima di avviare il sistema.

---

## File di configurazione

```
Tesi-FTD/
├── api_gateway/.env
├── orchestrator/.env
├── model_service/.env
├── llm_service/.env
└── nextflow_worker/.env  (opzionale — variabili iniettate via docker-compose.yml)
```

Copia i file di esempio per iniziare:
```bash
cp api_gateway/.env.example    api_gateway/.env
cp orchestrator/.env.example   orchestrator/.env
cp model_service/.env.example  model_service/.env
cp llm_service/.env.example    llm_service/.env
```

---

## 1. api_gateway/.env

```env
SECRET_KEY=cambia-questa-con-una-stringa-casuale-lunga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variabile | Obbligatoria | Descrizione |
|-----------|-------------|-------------|
| `SECRET_KEY` | **Sì** | Chiave condivisa per firma JWT — deve corrispondere a `orchestrator/.env` |
| `ALGORITHM` | No | Algoritmo JWT (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | TTL token in minuti (default: 30) |

---

## 2. orchestrator/.env

```env
SECRET_KEY=cambia-questa-con-una-stringa-casuale-lunga
DATABASE_URL=sqlite:////shared_db/clinical_twin.db
MODEL_SERVICE_URL=http://model_service:8000
NEXTFLOW_WORKER_URL=http://nextflow_worker:8000
SHARED_VOLUME_DIR=/shared_data
USE_MOCK=false
TEST_MODE=false
```

| Variabile | Obbligatoria | Descrizione |
|-----------|-------------|-------------|
| `SECRET_KEY` | **Sì** | Deve corrispondere a `api_gateway/.env` |
| `USE_MOCK` | No | `true` = usa MockRunner (nessun Nextflow, CSV sintetico) |
| `TEST_MODE` | No | `true` = attiva `mock_freesurfer` in Nextflow (30s invece di 6–8h) |

### USE_MOCK vs TEST_MODE

| Flag | Cosa fa | Quando usarlo |
|------|--------|--------------|
| `USE_MOCK=true` | Salta completamente Nextflow, genera CSV sintetico | Test unitari logica orchestratore |
| `TEST_MODE=true` | Esegue Nextflow reale ma rimpiazza FreeSurfer con mock sintetico | Test integrazione pipeline veloce |
| Entrambi `false` | Pipeline completa con FreeSurfer | Uso in produzione |

---

## 3. model_service/.env

```env
MLFLOW_TRACKING_URI=https://dagshub.com/tuo-username/Tesi-FTD.mlflow
MLFLOW_TRACKING_USERNAME=tuo-username-dagshub
MLFLOW_TRACKING_PASSWORD=tuo-token-dagshub
R_ENGINE_URL=http://inference_engine:8000/infer
SHARED_VOLUME_DIR=/shared_data
```

**Catena di fallback modello** (quando MLflow non è disponibile):
1. `/shared_data/models/{model_name}/model.rds`
2. `/app/model.rds` (bind-mount da `model_service/model.rds`)
3. `/shared_data/models/model.rds`

---

## 4. llm_service/.env

```env
SECRET_KEY=cambia-questa-con-una-stringa-casuale-lunga
GROQ_API_KEY=gsk_...
```

---

## 5. Variabili pipeline Nextflow (docker-compose.yml)

Queste variabili sono iniettate nel container `nextflow_worker`:

| Variabile | Descrizione |
|-----------|-------------|
| `SHARED_VOLUME_DIR` | Path volume condiviso dentro il container |
| `HOST_SHARED_VOLUME_DIR` | Path volume condiviso sull'**host** (DooD) |
| `NF_OUTDIR` | Directory output pipeline Nextflow |
| `NF_LABELS` | Path a `ROI_labels.tsv` (78 etichette regioni cerebrali) |
| `NF_SETTINGS` | Path a `pyradiomics.yaml` (parametri estrazione radiomica) |
| `MIG_DEVICE` | UUID istanza NVIDIA MIG per FastSurfer GPU. Lascia `all` per GPU standard |

---

## 6. Configurazione GPU

### GPU NVIDIA standard
Nessuna configurazione extra. FastSurfer usa tutte le GPU disponibili (`MIG_DEVICE=all`).

### NVIDIA MIG (Multi-Instance GPU)
Per sistemi HPC con GPU partitioning:
```bash
nvidia-smi -L  # trova l'UUID dell'istanza MIG
# Imposta in docker-compose.yml: MIG_DEVICE=MIG-GPU-xxxxxxxx-...
```

### Modalità CPU-only
Usa `brain_segmenter=freesurfer` (basato su CPU, nessuna GPU richiesta).

---

## 7. Licenza FreeSurfer

Il file licenza FreeSurfer deve essere presente in:
```
nextflow_worker/license.txt
```

Registrazione gratuita: https://surfer.nmr.mgh.harvard.edu/registration.html

Il file viene copiato automaticamente in `/tmp/nextflow_work/license.txt`
all'avvio del `nextflow_worker` (hook lifespan in `main.py`), che è il path
referenziato da `nextflow.config` per i bind-mount DooD.
