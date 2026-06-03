# Architettura del Sistema — MLOps

## Panoramica

MLOps è una piattaforma distribuita per la diagnosi differenziale della
Demenza Frontotemporale (FTD) basata su radiomica di MRI T1.
Il sistema segue un'architettura a microservizi con 7 servizi containerizzati
orchestrati tramite Docker Compose.

---

## Mappa dei servizi

```
┌─────────────────────────────────────────────────────────────────┐
│                    clinical_twin_net (bridge)                    │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   frontend   │    │   api_gateway    │    │  llm_service  │  │
│  │  React/Vite  │    │  FastAPI + JWT   │    │ FastAPI + LLM │  │
│  │  porta: 5173 │    │  porta: 8006(h)  │    │ porta: 8002(h)│  │
│  └──────┬───────┘    └────────┬─────────┘    └───────────────┘  │
│         │                    │                                   │
│         │            ┌───────▼──────────┐                       │
│         └───────────►│   orchestrator   │                       │
│                      │    FastAPI       │                       │
│                      │  porta: 8001(h)  │                       │
│                      └──┬──────────┬───┘                       │
│                         │          │                            │
│              ┌──────────▼──┐  ┌────▼────────────┐             │
│              │model_service│  │nextflow_worker  │             │
│              │FastAPI+MLflow│  │ FastAPI+Nextflow │             │
│              │porta: 8003(h)│  │  porta: 8005(h) │             │
│              └──────┬───────┘  └────────┬────────┘             │
│                     │                   │ DooD                  │
│              ┌──────▼────────┐    ┌─────▼──────────────────┐  │
│              │inference_engine│   │  Docker daemon (HOST)   │  │
│              │  R + Plumber   │   │  clinical-freesurfer    │  │
│              │ porta: 8004(h) │   │  clinical-fsl           │  │
│              └────────────────┘   │  clinical-pyradiomics   │  │
│                                   │  ftd-training           │  │
│                                   └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

(h) = porta host su loopback 127.0.0.1
```

---

## Dettaglio dei servizi

| Servizio | Tecnologia | Porta (host) | Ruolo |
|----------|-----------|-------------|-------|
| `frontend` | React 18 + Vite + TailwindCSS | 5173 | Dashboard clinica: upload MRI, storico task, visualizzazione UMAP 3D |
| `api_gateway` | FastAPI + SQLite | 127.0.0.1:8006 | Autenticazione JWT, gestione utenti |
| `orchestrator` | FastAPI + SQLite | 127.0.0.1:8001 | Gestione task asincroni, coordinamento pipeline |
| `model_service` | FastAPI + MLflow | 127.0.0.1:8003 | Download modello champion da DagsHub, trigger inferenza R |
| `inference_engine` | R + Plumber + uwot | 127.0.0.1:8004 | Inferenza XGBoost, calcolo embedding UMAP 3D |
| `llm_service` | FastAPI + Claude/Groq | 127.0.0.1:8002 | Assistente AI per interpretazione clinica |
| `nextflow_worker` | FastAPI + Nextflow | 127.0.0.1:8005 | Coordinatore pipeline neuroimaging (DooD) |

---

## Flusso dati end-to-end

```
Utente (browser)
    │ HTTP POST multipart (file NIfTI)
    ▼
Frontend :5173
    │ POST /analyze/upload + JWT
    ▼
API Gateway :8006  ──► valida JWT
    │
    ▼
Orchestrator :8001
    │  Fase 0: GET /model_info/HC_vs_bvFTD → tag brain_segmenter
    │  Fase 1: POST /start_preprocessing → nextflow_worker
    │  Fase 2: POST /infer → model_service
    │
    ├──► Nextflow Worker :8005
    │        │ subprocess: nextflow run preprocessing.nf
    │        │ DooD: daemon Docker avvia 4 container sull'HOST
    │        │
    │        ├── clinical-freesurfer: recon-all (6–8h CPU / 30s mock)
    │        ├── clinical-freesurfer: mri_convert  → nu.nii + aparc+aseg.nii
    │        ├── clinical-fsl: fslmaths × 78       → ROI/*.nii.gz
    │        └── clinical-pyradiomics              → radiomics_features.csv
    │               → /shared_data/features/features_17.csv
    │
    └──► Model Service :8003
             │ Scarica xgb.rds da DagsHub (o fallback locale)
             └──► Inference Engine :8004 (R/Plumber)
                      │ Predice HC/bvFTD + confidenza
                      │ Calcola UMAP 3D
                      └──► result_17.json → /shared_data/results/
```

---

## DooD (Docker-out-of-Docker)

Il `nextflow_worker` usa il pattern **Docker-out-of-Docker**:
monta il socket Docker dell'host per avviare i container della pipeline
direttamente sul **daemon Docker dell'host**.

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock  # DooD
  - /tmp/nextflow_work:/tmp/nextflow_work       # directory lavoro condivisa
```

Il path `/tmp/nextflow_work` è il punto di coordinamento per la licenza
FreeSurfer e la work directory di Nextflow.

---

## Volume condiviso: clinical_twin_shared_data

```
/shared_data/
├── nifti/                    # File MRI caricati
├── features/                 # CSV feature radiomiche (features_{task_id}.csv)
├── results/                  # Risultati inferenza (result_{task_id}.json)
├── models/HC_vs_bvFTD/       # Modello scaricato da MLflow
└── ROI_labels.tsv            # Copiato da nextflow_worker al boot
```

---

## Integrazione MLflow / DagsHub

Il modello XGBoost viene salvato in formato **extended model** da `XGBoost.r`:
- `$booster`: raw `xgb.Booster` (nessuna dipendenza `mlr`)
- `$trainingData`: training set con fattore `.outcome` (HC/bvFTD)
- `$x`, `$y`: dati per costruire lo spazio UMAP storico

La catena di fallback in `model_service` è:
1. Download da DagsHub MLflow (`models:/HC_vs_bvFTD@champion`)
2. `/shared_data/models/{model_name}/model.rds`
3. `/app/model.rds` (bind-mount locale)

---

## Sicurezza di rete

Tutti i servizi (eccetto il frontend) si legano a `127.0.0.1`, impedendo
l'accesso da rete esterna senza un reverse proxy. Il database SQLite è
condiviso tra `api_gateway` e `orchestrator` tramite volume named `clinical_twin_db`.
