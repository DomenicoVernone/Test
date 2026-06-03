# API Reference — Clinical Twin

La piattaforma Clinical Twin espone API REST su 5 microservizi.
Tutti i servizi comunicano sulla rete Docker `clinical_twin_net`.
L'accesso esterno è vincolato a `127.0.0.1` (solo loopback).

---

## Porte dei servizi

| Servizio | Porta container | Porta host (esterna) | Swagger UI |
|----------|----------------|----------------------|------------|
| api_gateway | 8000 | `127.0.0.1:8006` | http://localhost:8006/docs |
| orchestrator | 8000 | `127.0.0.1:8001` | http://localhost:8001/docs |
| model_service | 8000 | `127.0.0.1:8003` | http://localhost:8003/docs |
| llm_service | 8000 | `127.0.0.1:8002` | http://localhost:8002/docs |
| inference_engine (R/Plumber) | 8000 | `127.0.0.1:8004` | — |
| nextflow_worker | 8000 | `127.0.0.1:8005` | http://localhost:8005/docs |

---

## Autenticazione

Tutti gli endpoint (eccetto `/signup`, `/login`, `/health`) richiedono un JWT Bearer token.

### Ottenere un token

```bash
curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tuapassword"}'
```

Risposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Usa il token nelle richieste successive:
```
Authorization: Bearer <access_token>
```

I token JWT sono firmati con `HS256` usando la `SECRET_KEY` condivisa tra
`api_gateway` e `orchestrator`. Scadenza predefinita: 30 minuti.

---

## 1. API Gateway — porta 8006

### POST /signup
Registra un nuovo utente.

```bash
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"securepass"}'
```

Risposta `200`:
```json
{"message": "User created successfully"}
```

### POST /login
Autentica e riceve un token JWT.

```bash
curl -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"securepass"}'
```

Risposta `200`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET /me
Restituisce le informazioni dell'utente autenticato.

```bash
curl http://localhost:8006/me \
  -H "Authorization: Bearer <token>"
```

Risposta `200`:
```json
{"username": "doctor01"}
```

### GET /health
```json
{"status": "ok", "service": "api_gateway"}
```

---

## 2. Orchestrator — porta 8001

### POST /analyze/upload
Carica un file NIfTI e avvia la pipeline diagnostica completa.

```bash
curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/scan.nii.gz" \
  -F "model_name=HC_vs_bvFTD"
```

Risposta `202`:
```json
{
  "task_id": 17,
  "status": "PENDING",
  "filename": "a3f8b21c_scan.nii.gz",
  "model_name": "HC_vs_bvFTD"
}
```

> **Nota:** Il filename è prefissato con un hash MD5 di 8 caratteri per evitare collisioni.

### GET /analyze/status/{task_id}
Verifica lo stato e recupera i risultati quando completato.

```bash
curl http://localhost:8001/analyze/status/17 \
  -H "Authorization: Bearer <token>"
```

Risposta in esecuzione:
```json
{
  "task_id": 17,
  "status": "PROCESSING",
  "progress": 10.0,
  "filename": "a3f8b21c_scan.nii.gz"
}
```

Risposta completato (`status = "COMPLETED"`):
```json
{
  "task_id": 17,
  "status": "COMPLETED",
  "progress": 100.0,
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [
      {"x": -1.23, "y": 0.45, "z": 2.11, "label": "HC", "subject_id": "Paziente_Storico_1"}
    ],
    "nuovo_paziente": {"x": -0.91, "y": 0.38, "z": 1.74}
  }
}
```

**Valori di stato del task:**

| Stato | Significato |
|-------|------------|
| `PENDING` | Task creato, pipeline non ancora avviata |
| `PROCESSING` | Pipeline Nextflow in esecuzione (estrazione feature) |
| `ANALYZING_R` | Motore di inferenza R in esecuzione |
| `COMPLETED` | Diagnosi disponibile |
| `ERROR` | Pipeline fallita |

### GET /analyze/tasks
Lista tutti i task dell'utente autenticato.

### GET /analyze/nifti/{task_id}/volume.nii.gz
Scarica il file NIfTI associato a un task (usato dal viewer 3D).

### GET /health
```json
{"status": "ok", "service": "orchestrator"}
```

---

## 3. Model Service — porta 8003

### POST /infer
Scarica il modello champion da MLflow e avvia l'inferenza R.

```bash
curl -X POST http://localhost:8003/infer \
  -H "Content-Type: application/json" \
  -d '{"task_id": 17, "model_name": "HC_vs_bvFTD"}'
```

Risposta `200`:
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

Catena di fallback MLflow (in ordine se MLflow/DagsHub non disponibile):
1. `/shared_data/models/{model_name}/model.rds`
2. `/app/model.rds`
3. `/shared_data/models/model.rds`

### GET /model_info/{model_name}
Recupera i metadati del modello champion (chiamato dall'orchestratore prima
del preprocessing per determinare quale segmentatore cerebrale è stato usato
durante il training).

```bash
curl http://localhost:8003/model_info/HC_vs_bvFTD
```

Risposta `200`:
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

## 4. Inference Engine (R/Plumber) — porta 8004

Il motore di inferenza è un server R Plumber. È chiamato **solo da model_service**,
mai direttamente dall'utente.

### GET /health
```json
{"status": "ok"}
```

### POST /infer
Esegue l'inferenza clinica e calcola l'embedding UMAP 3D.

Parametri (body JSON): `task_id`, `model_name`, `model_dir` (path assoluto del file `.rds`)

Risposta:
```json
{
  "status": "success",
  "task_id": "17",
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [{"x": -1.23, "y": 0.45, "z": 2.11, "label": "HC", "subject_id": "..."}],
    "nuovo_paziente": {"x": -0.91, "y": 0.38, "z": 1.74}
  }
}
```

---

## 5. Nextflow Worker — porta 8005

Questo servizio è chiamato **solo dall'orchestratore**, non direttamente dall'utente.

### POST /start_preprocessing
Avvia la pipeline Nextflow di preprocessing per un file NIfTI.

`test_mode: true` attiva `mock_freesurfer` (bypassa FreeSurfer recon-all,
completa in ~30 secondi invece di 6–8 ore).

### GET /status/{task_id}
Verifica lo stato della pipeline Nextflow: `RUNNING`, `SUCCESS`, `FAILED`.

### GET /health
```json
{"status": "ok", "service": "nextflow_worker"}
```

---

## 6. LLM Service — porta 8002

### POST /chat
Chiede all'assistente AI un'interpretazione clinica.

### GET /health
```json
{"status": "ok", "service": "llm_service"}
```

---

## Gestione degli errori

Tutti i servizi restituiscono codici HTTP standard:

| Codice | Significato |
|--------|------------|
| `200` | Successo |
| `202` | Accettato (task asincrono avviato) |
| `401` | Non autorizzato (JWT mancante o non valido) |
| `404` | Risorsa non trovata |
| `422` | Errore di validazione (corpo della richiesta non valido) |
| `500` | Errore interno del server |

---

## Contratto dati: radiomics_features.csv

L'artefatto dati centrale scambiato tra `nextflow_worker` e `inference_engine`:

- Generato da: processo `feature_extraction` in `preprocessing.nf`
- Posizione: `/shared_data/features/features_{task_id}.csv`
- Formato: CSV con una riga per soggetto, ~6.864 colonne
- Nomi colonne: `{nome_ROI}_{feature_pyradiomics}` (es. `Hippocampus_original_shape_Volume`)
- Nomi ROI da: `ROI_labels.tsv` (78 regioni cerebrali)
