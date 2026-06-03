# Componenti e Struttura del Progetto — MLOps

---

## Struttura del repository

```
Tesi-FTD/
├── api_gateway/                    # Servizio autenticazione JWT
│   ├── main.py
│   ├── Dockerfile
│   └── .env.example
│
├── orchestrator/                   # Gestione task e coordinamento pipeline
│   ├── main.py
│   ├── core/
│   │   ├── config.py               # Impostazioni (SECRET_KEY, TEST_MODE, USE_MOCK...)
│   │   └── database.py
│   ├── services/
│   │   ├── pipeline.py             # run_full_pipeline() — pipeline 3 fasi
│   │   ├── nextflow_runner.py      # Client HTTP per nextflow_worker
│   │   └── mock_runner.py          # MockRunner per USE_MOCK=true
│   ├── routers/
│   │   └── analyze.py              # POST /analyze/upload, GET /analyze/status/{id}
│   ├── Dockerfile
│   └── .env.example
│
├── model_service/                  # Download modello MLflow + trigger inferenza R
│   ├── main.py                     # POST /infer, GET /model_info/{nome}
│   ├── services/
│   │   └── inference.py            # InferenceOrchestrator (MLflow + fallback)
│   ├── model.rds                   # Modello locale di fallback
│   └── Dockerfile
│
├── inference_engine/               # Inferenza statistica R (Plumber)
│   ├── api.R                       # GET /health, POST /infer (router Plumber)
│   ├── R/
│   │   └── inference_logic.R       # Inferenza XGBoost + calcolo UMAP 3D
│   ├── model.rds                   # Modello locale di fallback
│   └── Dockerfile
│
├── llm_service/                    # Assistente AI clinico
│   ├── main.py
│   └── Dockerfile
│
├── frontend/                       # Dashboard clinica React
│   ├── src/
│   │   ├── components/clinical/
│   │   │   ├── TaskHistory.jsx     # Lista task (polling + LiveTimer)
│   │   │   └── UmapViewer.jsx      # Visualizzazione UMAP 3D
│   │   └── hooks/
│   │       └── useTaskPolling.js   # Auto-aggiornamento stato task
│   └── Dockerfile
│
├── nextflow_worker/                # Worker pipeline neuroimaging (DooD)
│   ├── main.py                     # FastAPI: POST /start_preprocessing, GET /status/{id}
│   ├── nextflow/
│   │   ├── preprocessing.nf        # Pipeline principale: segmentazione → radiomica
│   │   ├── training.nf             # Pipeline training: merge → select → train
│   │   ├── main.nf                 # [NUOVO] Entry point canonico DSL2
│   │   ├── nextflow.config         # Config Docker, parametri default
│   │   └── configs/
│   │       ├── pyradiomics.yaml    # Impostazioni estrazione radiomica
│   │       ├── hyperparameters.yaml # Parametri nested CV (dataset completo)
│   │       ├── hyperparameters_small.yaml # [NUOVO] Parametri test veloci (12 soggetti)
│   │       └── training.config     # [NUOVO] Override configurazione training
│   ├── ftd_diagnosis/
│   │   ├── util/
│   │   │   ├── merge_radiomics.r   # Merge CSV feature in feat_all.csv
│   │   │   ├── process_metrics.r   # Aggregazione metriche CV
│   │   │   └── stability.r         # Analisi frequenza/stabilità feature
│   │   ├── sequential/
│   │   │   ├── RFE.r               # Selezione feature RFE + training sequenziale
│   │   │   └── lasso.r             # Selezione feature LASSO + training sequenziale
│   │   └── parallel/
│   │       ├── features_selection.r # LASSO/RFE per training parallelo
│   │       └── models/
│   │           ├── XGBoost.r       # XGBoost con nested CV + logging MLflow
│   │           ├── random_forest.r
│   │           ├── svm.r
│   │           └── kNN.r
│   ├── data/external/
│   │   └── ROI_labels.tsv          # 78 etichette regioni cerebrali (Index, Label)
│   ├── dockerfiles/                # Dockerfile per immagini pipeline
│   └── docker-compose.yml          # Compose solo per build immagini pipeline
│
├── docs/                           # Documentazione MkDocs
│   ├── docs/                       # File Markdown sorgente
│   ├── mkdocs.yml
│   ├── TECHNICAL_REPORT.md
│   ├── CHANGES_AND_PERFORMANCE.md
│   └── REPORT_FINALE_COMPLETO.md
│
└── docker-compose.yml              # Stack principale (7 servizi)
```

---

## Riepilogo microservizi

| Servizio | Nome container | Porta host | Tecnologia |
|----------|--------------|-----------|-----------|
| `api_gateway` | `clinical_api_gateway` | 127.0.0.1:8006 | FastAPI + SQLite + JWT |
| `orchestrator` | `clinical_orchestrator` | 127.0.0.1:8001 | FastAPI + SQLAlchemy |
| `model_service` | `clinical_model_service` | 127.0.0.1:8003 | FastAPI + MLflow |
| `llm_service` | `clinical_llm_service` | 127.0.0.1:8002 | FastAPI + Groq/Claude |
| `inference_engine` | `inference_engine` | 127.0.0.1:8004 | R + Plumber + uwot + xgboost |
| `frontend` | `clinical_frontend` | 5173 | React 18 + Vite + TailwindCSS |
| `nextflow_worker` | `nextflow_worker` | 127.0.0.1:8005 | FastAPI + Nextflow + DooD |

---

## Volumi Docker

| Volume | Mount point | Condiviso tra |
|--------|------------|--------------|
| `clinical_twin_shared_data` | `/shared_data` | orchestrator, model_service, inference_engine, llm_service, nextflow_worker |
| `clinical_twin_db` | `/shared_db` | api_gateway, orchestrator |
| `/tmp/nextflow_work` (bind) | `/tmp/nextflow_work` | nextflow_worker ↔ daemon Docker host |
| `/var/run/docker.sock` (bind) | `/var/run/docker.sock` | nextflow_worker → daemon Docker host (DooD) |

---

## File chiave aggiunti nelle sessioni 2026-05-27/28

| File | Tipo | Scopo |
|------|------|-------|
| `nextflow_worker/nextflow/main.nf` | Nuovo | Entry point canonico DSL2 per esecuzioni manuali/CI |
| `nextflow_worker/nextflow/configs/training.config` | Nuovo | Override parametri pipeline training (separazione config/codice) |
| `nextflow_worker/nextflow/configs/hyperparameters_small.yaml` | Nuovo | Parametri nested CV ridotti per dataset test a 12 soggetti |

---

## Comunicazione tra servizi

```
Frontend ──HTTP──► API Gateway ──HTTP──► Orchestrator
                                             │
                              ┌──────────────┼──────────────┐
                              │              │              │
                       Model Service  Nextflow Worker   (polling)
                              │              │
                      Inference Engine  [Docker daemon]
                                            │
                                    [4 container pipeline]
```

Scambio dati:
- REST API (HTTP/JSON): flusso di controllo e coordinamento task
- Volume Docker condiviso (`/shared_data`): file grandi (NIfTI, CSV, modelli, risultati)
- Socket Docker (`/var/run/docker.sock`): DooD — nextflow_worker avvia container sull'host

---

## Formato ROI_labels.tsv

Il file `nextflow_worker/data/external/ROI_labels.tsv` definisce le 78 regioni cerebrali:

```tsv
Index	Label
1	Left-Cerebral-White-Matter
2	Left-Cerebral-Cortex
...
78	Right-Cerebral-Cortex
```

Questo file viene:
1. Copiato in `/shared_data/ROI_labels.tsv` all'avvio di `nextflow_worker`
2. Usato da `roi_creator` (fslmaths) per creare le maschere binarie
3. Usato da `merge_radiomics.r` per costruire i nomi dei file CSV feature
4. Usato da `inference_logic.R` per il mapping ROI→colonne feature
5. **Deve** essere analizzato con `header=TRUE, sep="\t"`
