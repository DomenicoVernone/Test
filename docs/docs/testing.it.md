# Testing — Clinical Twin

---

## Riepilogo test

Tutti i test sono stati eseguiti sul branch `main` (commit `b08aab0`).

| Test | Modalità | Stato | Durata | Risultato |
|------|---------|-------|--------|-----------|
| Pipeline (dati sintetici) | TEST_MODE=true | ✅ PASSED | ~12 min | HC, 79.57% |
| Pipeline completa (MRI reale) | FreeSurfer CPU | ✅ PASSED | ~4h 21m | HC, 79.57% |
| Fallback MLflow | No connessione DagsHub | ✅ PASSED | — | Modello locale usato |
| Mock runner (USE_MOCK) | USE_MOCK=true | ✅ PASSED | ~2 min | CSV sintetico |

---

## Test 1: Pipeline sintetica (TEST_MODE=true)

**Scopo:** Verificare la pipeline completa senza attendere FreeSurfer (~8h).

**Input:** `sub-01_ses-test_T1w.nii` (MRI T1 reale)

**Risultati (Task 17):**
```json
{
  "status": "COMPLETED",
  "diagnosi_predetta": "HC",
  "confidenza": 0.7957,
  "plot_data": {
    "storico": [12 punti — 6 HC + 6 bvFTD],
    "nuovo_paziente": {"x": ..., "y": ..., "z": ...}
  }
}
```

**Tempi:**
- `mock_freesurfer`: ~30 secondi
- `nifti_converter`: ~10 secondi
- `roi_creator` (78 ROI): ~3 minuti
- `feature_extraction` (4 worker): ~8 minuti
- Inferenza R + UMAP 3D: ~45 secondi
- **Totale: ~12 minuti**

---

## Test 2: MRI reale (FreeSurfer CPU)

**Input:** `sub-01_ses-test_T1w.nii` (stesso file, TEST_MODE=false)

**Risultati:** Identici al Test 1 (HC, 79.57%).

**Tempi:**
- FreeSurfer `recon-all`: 4 ore 21 minuti
- Step rimanenti: ~12 minuti
- **Totale: ~4 ore 33 minuti**

---

## Bug fix applicati durante i test

20 bug identificati e corretti in 2 sessioni di sviluppo.

### Categorie di causa radice

| Categoria | Bug | Impatto |
|-----------|-----|---------|
| Parsing ROI_labels.tsv (`header=FALSE, sep=""`) | 2 | Tutti i mapping ROI sbagliati → feature zero → predizioni prive di significato |
| Path DooD disallineati (licenza FreeSurfer) | 3 | FreeSurfer crash all'avvio |
| Nomi immagini Docker errati | 1 | Tutti i processi Nextflow impossibili da avviare |
| Formato modello XGBoost incompatibile | 1 | Inferenza sempre in crash |
| `cbind` righe disallineate (multi-soggetto) | 1 | Training impossibile su dataset reali |
| Catena propagazione `test_mode` spezzata | 3 | Modalità mock mai attivata nonostante `TEST_MODE=true` |
| tryCatch annidato mancante | 1 | HTTP 500 invece di fallback "Sconosciuto" |
| Label cliniche hardcoded ("Malato"/"Sano") | 1 | Label sbagliate nell'output |
| Parsing filename (UUID vs MD5[:8]) | 1 | Lista task mostrава filename illeggibili |

### Fix critici (P1)

**1. Parsing etichette ROI** (`merge_radiomics.r`, `inference_logic.R`):
```r
# Prima (rotto): header=FALSE, sep="" → colonna V3 inesistente
# Dopo (corretto): header=TRUE, sep="\t" → colonna Label corretta
roi <- read.table(path, header = TRUE, sep = "\t")
roi_names <- roi$Label
```

**2. Path licenza FreeSurfer** (`nextflow.config`):
```groovy
# Prima: ${baseDir}/license.txt (path interno container, non visibile al daemon Docker host)
# Dopo:  /tmp/nextflow_work/license.txt (path host via bind-mount)
runOptions = "-v /tmp/nextflow_work/license.txt:/app/license.txt"
```

---

## Come ripetere i test

### Test rapido (TEST_MODE=true, ~15 min)

```bash
echo "TEST_MODE=true" >> orchestrator/.env
docker compose up --build -d
sleep 30

# Registra e accedi
curl -X POST http://localhost:8006/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

TOKEN=$(curl -s -X POST http://localhost:8006/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Carica una MRI
curl -X POST http://localhost:8001/analyze/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your_scan.nii" \
  -F "model_name=HC_vs_bvFTD"

# Controlla lo stato
curl http://localhost:8001/analyze/status/1 -H "Authorization: Bearer $TOKEN"
```

---

## Limitazioni note

### Modello attuale (dati di training sintetici)

Il modello `HC_vs_bvFTD` deployato è addestrato su **12 soggetti sintetici**
(6 HC + 6 bvFTD generati da 1 scan reale + rumore gaussiano).

| Limitazione | Impatto |
|------------|---------|
| 12 soggetti sintetici | Il modello non generalizza a pazienti reali |
| Nessuna selezione feature | ~6.864 feature usate senza selezione LASSO/RFE |
| Confidenza non calibrata | 79.57% non è una probabilità clinicamente interpretabile |
| Spazio UMAP con 12 punti | Visualizzazione non significativa clinicamente |
| Solo classificazione binaria (HC vs bvFTD) | Altri varianti FTD non coperti |

### Infrastruttura

| Limitazione | Stato |
|-----------|-------|
| Stato task in memoria (nextflow_worker) | Perso al riavvio del container |
| Nessun HTTPS | Solo HTTP (aggiungere nginx/caddy per produzione) |
| JWT senza refresh token | Sessioni da 30 min, richiede re-login |
| Nessun monitoring/alerting | Nessuna integrazione Prometheus/Grafana |
| DICOM non supportato | Solo NIfTI (.nii/.nii.gz) |

---

## Requisiti per la validazione clinica

1. Re-training del modello su dataset NIFD reale (≥200 soggetti)
2. Applicazione selezione feature LASSO/RFE
3. Calibrazione probabilità output (regressione isotonica o Platt scaling)
4. Coorte di validazione indipendente
5. Report: sensibilità, specificità, VPP, VPN, AUC-ROC
6. Revisione clinica da parte di neurologi
7. Conformità HIPAA/GDPR (anonimizzazione DICOM, cifratura dati)
