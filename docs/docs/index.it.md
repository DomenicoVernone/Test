# Clinical Twin — Piattaforma Radiomica FTD

**Clinical Twin** è una piattaforma MLOps per la diagnosi differenziale della
Demenza Frontotemporale (FTD) tramite analisi automatizzata di MRI T1.

---

## Cosa fa

Il sistema prende in input una MRI T1 e produce:

- **Diagnosi**: `HC` (Controllo Sano) o `bvFTD` (variante comportamentale FTD)
- **Punteggio di confidenza**: 0–100% (probabilità XGBoost)
- **Visualizzazione UMAP 3D**: posizione del paziente nello spazio clinico rispetto alla coorte di training

Tempo di analisi totale: **~12 minuti** (modalità test) o **~4–10 ore** (pipeline FreeSurfer completa).

---

## Architettura

7 microservizi containerizzati orchestrati tramite Docker Compose:

| Servizio | Porta | Ruolo |
|---------|------|-------|
| Frontend (React) | 5173 | Dashboard clinica |
| API Gateway | 127.0.0.1:8006 | Autenticazione JWT |
| Orchestrator | 127.0.0.1:8001 | Gestione task |
| Model Service | 127.0.0.1:8003 | MLflow + download modello |
| Inference Engine | 127.0.0.1:8004 | R + XGBoost + UMAP |
| LLM Service | 127.0.0.1:8002 | Assistente AI |
| Nextflow Worker | 127.0.0.1:8005 | Pipeline neuroimaging |

Vedi [Architettura del Sistema](SYSTEM_ARCHITECTURE.it.md) per il diagramma completo.

---

## Pipeline

```
MRI T1 (.nii.gz)
    → FreeSurfer recon-all (o mock_freesurfer per i test)
    → 78 maschere regioni cerebrali (FSL fslmaths)
    → Estrazione feature PyRadiomics (~6.864 feature)
    → Classificazione XGBoost + embedding UMAP 3D
    → Diagnosi + confidenza + visualizzazione
```

Vedi [Documentazione Pipeline](Pipeline_doc.it.md) per i dettagli completi.

---

## Avvio rapido

```bash
# 1. Clone
git clone https://github.com/carlosto033/Tesi-FTD.git && cd Tesi-FTD

# 2. Configura .env e aggiungi licenza FreeSurfer
cp api_gateway/.env.example api_gateway/.env
cp orchestrator/.env.example orchestrator/.env
cp /path/to/license.txt nextflow_worker/license.txt

# 3. Build immagini pipeline
docker compose -f nextflow_worker/docker-compose.yml build

# 4. Abilita modalità test per esecuzioni veloci (~12 min invece di ~8h)
echo "TEST_MODE=true" >> orchestrator/.env

# 5. Avvia
docker compose up --build -d

# 6. Apri dashboard: http://localhost:5173
```

Vedi [Guida Rapida](Guida_Rapida.it.md) per il walkthrough completo.

---

## Stato del sistema

| Componente | Stato |
|-----------|-------|
| Pipeline end-to-end | ✅ Funzionante (testato 2026-05-28) |
| TEST_MODE (mock FreeSurfer) | ✅ Funzionante (~12 min) |
| Pipeline FreeSurfer completa | ✅ Funzionante (~4h 21m misurati) |
| Inferenza XGBoost + UMAP 3D | ✅ Funzionante (HC, 79.57% su scan di test) |
| MLflow/DagsHub model registry | ✅ Funzionante (con fallback) |
| Modello attuale | ⚠️ Addestrato su 12 soggetti sintetici — solo ricerca |
| Validazione clinica | ❌ Richiede dataset NIFD reale |

---

## Documentazione

- [Architettura del Sistema](SYSTEM_ARCHITECTURE.it.md)
- [Componenti e Struttura](COMPONENTS_&_STRUCTURE.it.md)
- [Installazione](Installazione.it.md)
- [Configurazione](Configurazione.it.md)
- [Pipeline](Pipeline_doc.it.md)
- [Guida Rapida](Guida_Rapida.it.md)
- [API Reference](api.it.md)
- [Deployment](Deployment.it.md)
- [Testing](testing.it.md)
- [Report Tecnico](REPORT_FINALE_COMPLETO.md)
- [Changelog](CHANGES_AND_PERFORMANCE.md)
