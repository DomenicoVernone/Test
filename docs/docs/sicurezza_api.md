# API Security Test Report
**Progetto:** Clinical Twin — FTD Diagnosis System  
**Data:** 2026-06-04  
**Standard:** OWASP API Security Top 10 — 2023  
**Ambiente:** localhost, tutti i container attivi

---

## Configurazione testata

| Servizio | Porta | Container |
|---|---|---|
| API Gateway | 8006 | clinical_api_gateway |
| Orchestrator | 8001 | clinical_orchestrator |
| LLM Service | 8002 | clinical_llm_service |
| Model Service | 8003 | clinical_model_service |
| Inference Engine | 8004 | inference_engine |
| Nextflow Worker | 8005 | nextflow_worker |

---

## Tabella risultati

| # | Test | Esito | Note |
|---|---|---|---|
| F1 | Health check tutti i servizi | PARZIALE | 8001–8005: 200 OK. API Gateway: `/health` → 404, health è su `/` |
| F2 | Auth register + token | OK | POST `/signup` → 201, POST `/login` → JWT |
| F3 | GET /users/me | FAIL | Endpoint non esiste (404) — non implementato |
| F4 | GET /analyze/results/19 | FAIL | Endpoint non esiste — usare `/analyze/status/{id}` |
| F4b | GET /analyze/status/19 | OK | 200 con dati completi, diagnosi HC |
| F5 | LLM Service /health | OK | 200 |
| F6 | Model Service /model_info/HC_vs_bvFTD | OK | 200 con metadata MLflow |
| S1 | OWASP API1 — Object Auth (BOLA) | OK | task_id=1 → 404 "Task non trovato o non autorizzato" |
| S2 | OWASP API2 — Auth mancante | OK | 401 "Not authenticated" |
| S3 | OWASP API2 — Token falso | OK | 401 "Credenziali non valide o token scaduto" |
| S3b | OWASP API2 — JWT malformato | OK | 401 |
| S4 | OWASP API3 — Mass assignment (is_admin) | OK | Campo ignorato, utente creato senza privilegi admin |
| S5 | OWASP API4 — Rate limiting | **VULN** | 20 richieste consecutive → tutte 200. Nessun rate limit. |
| S6 | OWASP API5 — Admin endpoints | OK | `/admin`, `/admin/users` → 404 |
| S7 | OWASP API6 — Pipeline flood | **VULN** | 5 pipeline concorrenti → tutte accettate (200). Nessun limite. |
| S8 | OWASP API7 — SSRF (model_name URL) | **VULN** | `model_name=http://evil.com/malicious` accettato dal Orchestrator. Fallisce solo a runtime in R. |
| S9 | OWASP API8 — Security headers | **VULN** | `server: uvicorn` esposto. Mancano X-Frame-Options, X-Content-Type-Options, CSP, HSTS. Porte su 127.0.0.1: OK. |
| S10 | OWASP API9 — Debug/docs endpoints | **VULN** | `/docs`, `/redoc`, `/openapi.json` accessibili senza autenticazione su 8006 e 8001. |
| S11 | OWASP API10 — Path traversal | PARZIALE | `../../etc/passwd` → 422 (Pydantic blocca). Ma `task_id=999999` → 500 con stacktrace R interno esposto. |
| I1 | File non valido (.txt) | OK | 400 "Formato non supportato" |
| I2 | File vuoto (.nii.gz) | **VULN** | File vuoto accettato → task PENDING (dovrebbe essere 400) |
| I3 | JSON malformato | OK | 422 con dettagli validazione |
| I4 | SQL injection in username | OK | 401 — ORM protegge |
| I5 | XSS in username | **VULN** | `<script>alert(1)</script>` accettato e persistito (id=8). |

---

## Vulnerabilità — Dettaglio e Fix

### VULN-01 — Nessun Rate Limiting (S5, S7) `MEDIO`

**Rischio:** Un attaccante può inondare l'API con richieste arbitrarie o avviare decine di pipeline computazionalmente costose (Nextflow + R) senza limiti, causando DoS/resource exhaustion.

**Fix — API Gateway (FastAPI):**
```python
# pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("10/minute")
async def login(...): ...

@app.post("/analyze/")
@limiter.limit("3/minute")  # pipeline costose
async def analyze(...): ...
```

**Applicare su:** api_gateway `/login`, `/signup`; orchestrator `/analyze/`.

---

### VULN-02 — SSRF tramite model_name (S8) `ALTO`

**Rischio:** Il campo `model_name` non è validato prima di essere passato al Model Service e poi all'Inference Engine R. Un attaccante può iniettare URL arbitrari (`http://internal-service:8003/admin`, `file:///etc/passwd`) che vengono risolti dal container R sulla rete interna Docker.

**Fix — Orchestrator / Model Service:**
```python
ALLOWED_MODELS = {"HC_vs_bvFTD"}  # whitelist da config/DB

def validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(status_code=422, detail="Modello non riconosciuto")
    return model_name
```

Aggiungere la validazione prima di inoltrare la richiesta al model_service.

---

### VULN-03 — Security Headers mancanti (S9) `BASSO`

**Rischio:** `server: uvicorn` rivela il framework. L'assenza di X-Content-Type-Options, X-Frame-Options e CSP aumenta l'esposizione a clickjacking e MIME sniffing.

**Fix — middleware FastAPI (tutti i servizi):**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers.pop("server", None)
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

### VULN-04 — /docs e /openapi.json pubblici (S10) `MEDIO`

**Rischio:** Tutta la superficie API è documentata e accessibile senza autenticazione. In produzione questo facilita il discovery di endpoint e parametri da parte di attaccanti.

**Fix — disabilitare in produzione:**
```python
# In main.py — condizionale su env
import os

docs_url = "/docs" if os.getenv("ENV") == "development" else None
redoc_url = "/redoc" if os.getenv("ENV") == "development" else None
openapi_url = "/openapi.json" if os.getenv("ENV") == "development" else None

app = FastAPI(docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url)
```

---

### VULN-05 — Errore 500 con dettagli R interni (S11) `MEDIO`

**Rischio:** Quando `task_id` non esiste o R fallisce, l'API restituisce il messaggio di errore interno R (incluso il tipo di eccezione e traccia). Questo espone dettagli dell'architettura interna.

**Risposta attuale:**
```json
{"detail": "Inference engine R ha risposto con errore 500: {\"status\":[\"error\"],\"message\":[\"Errore durante l'inferenza R: cannot open the connection\"]}"}
```

**Fix — Model Service:**
```python
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        raise HTTPException(status_code=404, detail="Task o modello non trovato")
    # Log internamente, non esporre
    logger.error(f"Inference engine error: {e.response.text}")
    raise HTTPException(status_code=502, detail="Errore interno del servizio di inferenza")
```

---

### VULN-06 — File vuoto accettato (I2) `BASSO`

**Rischio:** Un file `.nii.gz` vuoto viene accettato e messo in coda. La pipeline fallirà a runtime con un errore interno invece di essere rifiutata in input.

**Fix — Orchestrator, validazione upload:**
```python
if file.size == 0:
    raise HTTPException(status_code=400, detail="Il file caricato è vuoto")
# oppure dopo il salvataggio:
if os.path.getsize(file_path) == 0:
    os.remove(file_path)
    raise HTTPException(status_code=400, detail="Il file caricato è vuoto")
```

---

### VULN-07 — XSS stored nel campo username (I5) `MEDIO`

**Rischio:** Username `<script>alert(1)</script>` viene persistito nel database. Se l'username viene renderizzato in una UI HTML senza escape (es. dashboard admin, log visualizer), si ottiene XSS stored.

**Fix — Schema Pydantic con validazione:**
```python
import re
from pydantic import validator

class UserCreate(BaseModel):
    username: str
    password: str

    @validator("username")
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.-]{3,50}$', v):
            raise ValueError("Username non valido: solo caratteri alfanumerici, _, ., -")
        return v
```

---

## Riepilogo per priorità

| Priorità | # | Vulnerabilità |
|---|---|---|
| ALTO | 1 | SSRF tramite model_name (VULN-02) |
| MEDIO | 4 | No rate limiting (VULN-01), /docs pubblici (VULN-04), 500 con errori interni (VULN-05), XSS stored (VULN-07) |
| BASSO | 2 | Security headers mancanti (VULN-03), file vuoto accettato (VULN-06) |

---

## Fix applicati — Riepilogo

| Fix | Vulnerabilità | Applicato | Testato | Risultato |
|---|---|---|---|---|
| F1 | SSRF model_name | `orchestrator/routers/analyze.py`, `model_service/main.py` | ✓ | `model_name=http://evil.com` → 422 |
| F2 | Rate limiting | `api_gateway/core/limiter.py`, `routers/auth.py`, `orchestrator/core/limiter.py`, `routers/analyze.py` | ✓ | 6° login → 429 |
| F3 | Docs pubblici | Tutti i `main.py` + `ENV=development` in `docker-compose.yml` | ✓ | /docs → 200 in dev, 404 in prod |
| F4 | Errori R nascosti | `model_service/main.py` (catch generico) | ✓ | 500 → "Errore durante l'inferenza. Riprova." |
| F5 | XSS username | `api_gateway/models/schemas.py` (field_validator) | ✓ | `<script>` → 422 |
| F6 | Security headers | Tutti i `main.py` (middleware) + `--no-server-header` nei Dockerfile | ✓ | `server: webserver`, X-Frame-Options, X-Content-Type-Options presenti |
| F7 | Validazione file MRI | `orchestrator/routers/analyze.py` (size + magic bytes) | ✓ | file vuoto → 422 |

---

## Gap funzionali rimanenti

| Endpoint atteso | Stato |
|---|---|
| `GET /users/me` (API Gateway) | Non implementato — 404 |

---

## JWT / BOLA / BFLA / Mass Assignment Hardening (2026-06-04)

### Security Score
- **Prima del fix:** 0/13 controlli OK
- **Dopo il fix:** 13/13 controlli OK

| # | Vulnerabilità | File | Testato | Risultato |
|---|---|---|---|---|
| JWT1 | Scadenza token 15min | api_gateway/core/config.py | ✓ | expires_in=900 — PASS |
| JWT2 | Refresh token implementato | api_gateway/routers/auth.py | ✓ | POST /refresh → 401 senza cookie — PASS |
| JWT3 | jti + blacklist logout | api_gateway/core/security.py, routers/auth.py | ✓ | logout → 204, token riusato → 401 "Token revocato" — PASS |
| JWT4 | SECRET_KEY >= 64 chars | api_gateway/.env, core/config.py | ✓ | 64 chars (`bb7a091739...`), validator attivo — PASS |
| JWT5 | sub = user_id numerico | api_gateway/core/security.py | ✓ | sub="1" (admin), sub="10" (userA) — numerico — PASS |
| BOLA | owner_id su tutti gli endpoint | orchestrator/routers/analyze.py | ✓ | task altrui → 404 "Task non trovato o non autorizzato" — PASS |
| BFLA1 | Sistema ruoli user/admin | api_gateway/models/domain.py | ✓ | UserRole enum con valori lowercase, colonna role — PASS |
| BFLA2 | /admin/* protetti da require_admin | api_gateway/routers/auth.py | ✓ | user normale → 403, admin → 200 — PASS |
| MA1 | Schema input/output separati | api_gateway/models/schemas.py | ✓ | UserResponse espone id/username/role, nessun password_hash — PASS |
| MA2 | role/is_admin ignorati da input | api_gateway/routers/auth.py | ✓ | signup con role=admin, is_admin=true → role="user" — PASS |
| HC1 | bcrypt rounds >= 12 | api_gateway/core/security.py | ✓ | bcrypt__rounds=12 — PASS |
| HC2 | Timing attack protection | api_gateway/core/security.py | ✓ | _DUMMY_HASH pre-calcolato, authenticate_user sempre esegue verify — PASS |
| HC3 | Password strength validation | api_gateway/models/schemas.py | ✓ | password "abc" (< 8 chars) → 422 con messaggio di errore — PASS |

### Note tecniche (fix applicati durante il test)

Durante l'esecuzione dei test sono stati identificati e risolti i seguenti problemi di avvio:

1. **SQLAlchemy Enum storage** — `Enum(UserRole)` di default salva il *nome* dell'enum (es. `"ADMIN"`) invece del *valore* (es. `"admin"`). Risolto aggiungendo `values_callable=lambda obj: [e.value for e in obj]` in `api_gateway/models/domain.py` e `orchestrator/models/domain.py`.

2. **_seed_admin crash** — La funzione controllava `filter(User.role == "admin")` ma il DB conteneva valori uppercase. Risolto aggiungendo controllo per username E correzione automatica del ruolo se errato.

3. **Migration di normalizzazione** — Aggiunta migrazione in `api_gateway/main.py` che normalizza i valori `ADMIN`→`admin` e `USER`→`user` nei dati esistenti.

---

## Auth Pages — Security Features (2026-06-09)

### Modifiche di sicurezza implementate

| # | Feature | File | Attacco prevenuto |
|---|---------|------|-------------------|
| AP1 | Errori login generici — mai rivela se username esiste o password è sbagliata | frontend/src/pages/Login.jsx | User enumeration |
| AP2 | Blocco client-side 60s dopo 3 tentativi falliti | frontend/src/pages/Login.jsx | Brute force login |
| AP3 | POST /forgot-password risponde sempre 200 con messaggio identico indipendentemente dall'email | api_gateway/routers/auth.py | Email enumeration |
| AP4 | POST /reset-password revoca tutti i JWT attivi dell'utente dopo il reset | api_gateway/routers/auth.py + core/security.py | Token hijacking post-reset |
| AP5 | POST /register — ruolo hardcoded a UserRole.USER lato server, mai dal client | api_gateway/routers/auth.py | Mass assignment su nuovo endpoint |
| AP6 | Token reset password scadenza 1 ora + marcato come "usato" dopo il primo utilizzo | api_gateway/models/domain.py | Riuso token reset |

### Endpoint implementati (precedentemente mancanti)

| Endpoint | Stato |
|---|---|
| `POST /forgot-password` | Implementato — 200 con risposta generica |
| `POST /reset-password` | Implementato — reset + revoca JWT |
| `POST /register` | Implementato — endpoint pubblico senza admin |

### Dettaglio tecnico

**AP1 — User enumeration protection**  
Prima: messaggi di errore differenziati ("utente non trovato" vs "password errata") permettevano di enumerare gli username validi.  
Dopo: risposta sempre generica "Credenziali non valide" in tutti i casi di errore 401/400.

**AP3 — Email enumeration protection**  
Il backend risponde sempre:  
`{"message": "Se l'email è registrata riceverai le istruzioni entro pochi minuti."}`  
Sia che l'email esista nel DB che non esista.  
Un attaccante non può scoprire quali email sono registrate nel sistema.

**AP4 — Token hijacking post-reset**  
Dopo reset password riuscito:
1. Nuova password salvata con bcrypt hash
2. Query su RevokedToken: inserisce i jti di tutti i token attivi dell'utente
3. Qualsiasi token precedente → 401 "Token revocato" al prossimo utilizzo
