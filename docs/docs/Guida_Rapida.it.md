# Guida Rapida — Clinical Twin

Questa guida descrive il percorso più veloce per eseguire la prima analisi MRI.

---

## Tempi stimati

| Modalità | Tempo totale | Caso d'uso |
|----------|-------------|-----------|
| **TEST_MODE=true** (mock FreeSurfer) | ~5–15 minuti | Sviluppo, test pipeline |
| **FreeSurfer CPU** (segmentazione reale) | ~4–10 ore | Produzione, ricerca |
| **FastSurfer GPU** (CUDA) | ~30–60 minuti | Produzione con GPU NVIDIA |

---

## Prerequisiti

1. Docker Desktop in esecuzione
2. Tutti i file `.env` configurati (vedi [Configurazione](Configurazione.it.md))
3. Licenza FreeSurfer in `nextflow_worker/license.txt`
4. Immagini Docker pipeline costruite: `docker compose -f nextflow_worker/docker-compose.yml build`

---

## Quickstart: Modalità Test (raccomandato per il primo avvio)

### Step 1 — Imposta TEST_MODE

Modifica `orchestrator/.env`:
```env
TEST_MODE=true
USE_MOCK=false
```

Questo attiva `mock_freesurfer`: invece di eseguire FreeSurfer `recon-all` (6–8 ore),
la pipeline genera maschere cerebrali sintetiche in ~30 secondi.

### Step 2 — Avvia il sistema

```bash
docker compose up --build -d
```

Attendi ~30 secondi che tutti i servizi siano pronti.

### Step 3 — Registra e accedi

Tramite browser: apri **http://localhost:5173** e accedi direttamente.

Tramite curl:
```bash
# Registra
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"test123"}'

# Accedi
curl -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor01","password":"test123"}'
```

### Step 4 — Carica una MRI

Tramite browser (raccomandato):
1. Apri http://localhost:5173
2. Clicca **"Carica MRI"** o **"Nuova Analisi"**
3. Seleziona un file `.nii` o `.nii.gz`
4. Scegli il modello `HC_vs_bvFTD`
5. Clicca **"Analizza"**

### Step 5 — Attendi i risultati

Il frontend **esegue polling automaticamente** ogni 3 secondi.
Vedrai la card del task passare da **IN ELABORAZIONE** → **COMPLETATO**.

Tempo totale con `TEST_MODE=true`: circa **5–15 minuti**.

### Step 6 — Visualizza i risultati

Quando completato, clicca la card del task nella barra laterale per vedere:
- **Diagnosi**: `HC` (Controllo Sano) o `bvFTD`
- **Confidenza**: es. 79.57%
- **UMAP 3D**: visualizzazione interattiva della posizione del paziente rispetto alla coorte di training

---

## Diagramma flusso completo

```
[Docker Desktop in esecuzione]
        │
        ▼
docker compose up --build -d
        │
        ▼
http://localhost:5173  ──► Login
        │
        ▼
Carica scan.nii.gz  ──► Seleziona modello: HC_vs_bvFTD
        │
        ▼
Orchestratore crea task (PENDING)
        │
        ▼
Fase 0: model_service → brain_segmenter = "freesurfer"
        │
        ▼
Fase 1: Pipeline Nextflow
  ├─ TEST_MODE=true  → mock_freesurfer (30s) → ROI → radiomica → CSV
  └─ TEST_MODE=false → FreeSurfer recon-all (6–8h) → ROI → radiomica → CSV
        │
        ▼
Fase 2: model_service → inference_engine (R)
  ├─ Predizione XGBoost: HC o bvFTD
  ├─ Confidenza: 0.00–1.00
  └─ UMAP 3D: spazio storico + nuovo paziente
        │
        ▼
Task → COMPLETATO (100%)
        │
        ▼
Frontend mostra: diagnosi + confidenza + visualizzazione 3D
```

---

## Modalità Produzione (FreeSurfer reale)

Per analizzare dati MRI reali:

1. Imposta `TEST_MODE=false` in `orchestrator/.env`
2. Carica una MRI T1 reale (`.nii` o `.nii.gz`)
3. La pipeline eseguirà FreeSurfer `recon-all` completo (~4–10 ore su CPU)
4. La card del task mostra un timer live durante l'elaborazione
5. I risultati appaiono automaticamente al completamento

> **Suggerimento:** Usa FastSurfer con una GPU per ridurre il tempo di segmentazione
> da ~8h a ~30 minuti. Imposta `MIG_DEVICE=all` e il sistema userà automaticamente
> FastSurfer se il modello deployato è stato addestrato con FastSurfer.

---

## Arresto

```bash
# Ferma senza perdere dati
docker compose down

# Ferma ed elimina tutti i volumi (ATTENZIONE: elimina tutto lo storico task)
docker compose down -v
```
