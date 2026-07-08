# Documentazione Sicurezza — Test e Modifiche al Codice

**Progetto:** Clinical Twin — MLOps Neuroimaging  
**Data:** 23 Giugno 2026  
**Autore:** Domenico Vernone  
**Standard di riferimento:** OWASP API Security Top 10 (2023)  
**Ambiente di test:** Docker Compose su Windows 11 Pro, Windows PowerShell

---

Questo documento descrive i 10 test di sicurezza eseguiti manualmente tramite `curl.exe`
su Windows PowerShell, le vulnerabilità simulate, i risultati ottenuti e le modifiche
al codice applicate per mitigare ciascuna vulnerabilità.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #1 — Token falso (JWT)
**OWASP:** API2 — Broken Authentication  
**File modificato:** `api_gateway/core/security.py` (riga 76–84) + `api_gateway/core/config.py` (riga 11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante costruisce un JWT contraffatto — ad esempio firmato con una chiave diversa
o con payload manomesso — e lo invia negli header di una richiesta autenticata.
Se il server non verifica la firma, accetta il token come valido e concede accesso.

### Comando di test eseguito
```powershell
curl.exe -X GET http://localhost:8001/analyze/ `
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTkiLCJ1c2VybmFtZSI6ImhhY2tlciIsInJvbGUiOiJhZG1pbiJ9.FIRMA_FALSA"
```

### Risultato ottenuto
✅ HTTP 401 — `{"detail":"Credenziali non valide o token scaduto"}`  
Il server rifiuta il token perché la firma non corrisponde alla `SECRET_KEY` interna.
Nessun dato viene restituito.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/core/security.py
def _decode_token(token: str) -> dict:
    # Nessuna gestione dell'eccezione: un token malformato
    # provocava un crash 500 anziché un rifiuto controllato 401
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```
```python
# api_gateway/core/config.py
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
```

**DOPO (codice sicuro):**
```python
# api_gateway/core/security.py  (riga 76–84)
def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide o token scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
```
```python
# api_gateway/core/config.py  (riga 11)
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
```

**Perché funziona:**  
`python-jose` lancia `JWTError` se la firma non corrisponde alla chiave segreta o se
il token è scaduto. Il blocco `try/except` intercetta questo errore e risponde con
HTTP 401 in modo controllato, senza esporre stack trace. La finestra di validità
ridotta a 15 minuti limita il tempo utile di un token eventualmente rubato.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #2 — Brute force / Rate limiting
**OWASP:** API4 — Unrestricted Resource Consumption  
**File modificato:** `api_gateway/core/limiter.py` (riga 1–4) + `api_gateway/routers/auth.py` (riga 99–101)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante invia rapidamente molte richieste di login con password diverse
(attacco a dizionario) sfruttando l'assenza di un limite al numero di tentativi.
Con un endpoint illimitato, è possibile provare migliaia di password al secondo.

### Comando di test eseguito
```powershell
for ($i = 1; $i -le 6; $i++) {
    Write-Host "Tentativo $i"
    curl.exe -X POST http://localhost:8006/login `
      -H "Content-Type: application/x-www-form-urlencoded" `
      -d "username=admin&password=WrongPass$i"
}
```

### Risultato ottenuto
✅ HTTP 429 al 6° tentativo — `{"error":"Rate limit exceeded: 5 per 1 minute"}`  
I primi 5 tentativi ricevono HTTP 401 (credenziali errate). Al sesto, slowapi
blocca la richiesta e restituisce 429 Too Many Requests.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/routers/auth.py
@router.post("/login", response_model=Token)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Nessun limite di frequenza: tentativi illimitati
    user = authenticate_user(form_data.username, form_data.password, db)
    ...
```

**DOPO (codice sicuro):**
```python
# api_gateway/core/limiter.py  (riga 1–4)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```
```python
# api_gateway/routers/auth.py  (riga 99–101)
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    ...
```

**Perché funziona:**  
`slowapi` è un wrapper di `limits` per FastAPI. Il decoratore `@limiter.limit("5/minute")`
conta le richieste per indirizzo IP (tramite `get_remote_address`) e restituisce HTTP 429
non appena si supera il limite. La `key_func` basata sull'IP impedisce che un singolo
client esaurisca le risorse del server o bruteforzi le credenziali.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #3 — BOLA (task di un altro utente)
**OWASP:** API1 — Broken Object Level Authorization  
**File modificato:** `orchestrator/routers/analyze.py` (riga 130–137)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
L'utente "userB" è autenticato con il proprio token JWT valido ma tenta di accedere
allo stato del task con ID 1, che appartiene a "userA". Se il server filtrasse solo
per `task_id` senza verificare il proprietario, qualsiasi utente potrebbe leggere
i risultati clinici di altri pazienti.

### Comando di test eseguito
```powershell
# userB tenta di accedere al task 1 (appartenente a userA)
$TOKEN_USER_B = "eyJ..."   # token JWT di userB
curl.exe -X GET http://localhost:8001/analyze/status/1 `
  -H "Authorization: Bearer $TOKEN_USER_B"
```

### Risultato ottenuto
✅ HTTP 404 — `{"detail":"Task non trovato o non autorizzato"}`  
Il server non espone l'esistenza del task: risponde 404 anche se il task esiste,
perché non appartiene all'utente autenticato. Nessun dato clinico viene esposto.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# orchestrator/routers/analyze.py
@router.get("/status/{task_id}")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Solo filtro per task_id — qualsiasi utente poteva leggere qualsiasi task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    ...
```

**DOPO (codice sicuro):**
```python
# orchestrator/routers/analyze.py  (riga 130–137)
@router.get("/status/{task_id}")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id   # <-- controllo di proprietà
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato o non autorizzato")
    ...
```

**Perché funziona:**  
Aggiungendo `Task.owner_id == current_user.id` alla query SQLAlchemy, il database
restituisce `None` se il task non appartiene all'utente corrente. Il 404 è intenzionale:
rispondere 403 rivelerebbe che il task esiste (information leakage). Stesso pattern
applicato a `GET /analyze/` (lista task) e `GET /analyze/nifti/{task_id}`.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #4 — XSS nel username
**OWASP:** API3 — Broken Object Property Level Authorization  
**File modificato:** `api_gateway/models/schemas.py` (riga 11–18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante registra un account con un username contenente codice JavaScript
(`<script>alert('XSS')</script>`). Se questo valore venisse salvato nel database
e successivamente restituito a un'interfaccia web senza sanitizzazione, si potrebbe
eseguire codice arbitrario nel browser di un amministratore che visualizza la lista utenti.

### Comando di test eseguito
```powershell
curl.exe -X POST http://localhost:8006/register `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"<script>alert(1)</script>\",\"password\":\"Test1234!\"}"
```

### Risultato ottenuto
✅ HTTP 422 — `{"detail":[{"msg":"Value error, Username non valido. Usa solo lettere, numeri, . _ - (3-50 caratteri)"}]}`  
Il payload XSS viene rifiutato a livello di validazione prima di raggiungere il database.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/models/schemas.py
class UserCreate(BaseModel):
    username: str       # Nessuna validazione: accettava qualsiasi stringa
    password: str
    email: Optional[str] = None
```

**DOPO (codice sicuro):**
```python
# api_gateway/models/schemas.py  (riga 6–18)
import re
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_safe(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_.\-]{3,50}$', v):
            raise ValueError(
                "Username non valido. Usa solo lettere, numeri, . _ - (3-50 caratteri)"
            )
        return v
```

**Perché funziona:**  
La regex `^[a-zA-Z0-9_.\-]{3,50}$` applica una whitelist di caratteri consentiti:
sono ammessi solo caratteri alfanumerici, underscore, punto e trattino. I caratteri
`<`, `>`, `"`, `'`, `;` — necessari per costruire payload XSS o SQL injection —
non sono nella whitelist e vengono rifiutati con HTTP 422 da Pydantic prima
che il dato raggiunga il layer applicativo o il database.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #5 — SSRF tramite model_name
**OWASP:** API7 — Server Side Request Forgery  
**File modificato:** `orchestrator/routers/analyze.py` (riga 20–29) + `model_service/main.py` (riga 17–25)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
L'attaccante invia un valore arbitrario nel campo `model_name` — ad esempio un URL
(`http://169.254.169.254/latest/meta-data/`) o un path di filesystem (`../../etc/passwd`).
Se il backend usa `model_name` direttamente per costruire percorsi o URL di download
da MLflow senza validazione, un attaccante può forzare il server a fare richieste
verso host interni o leggere file arbitrari.

### Comando di test eseguito
```powershell
# Ottieni prima un token valido
$resp = curl.exe -s -X POST http://localhost:8006/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=Admin1234!" | ConvertFrom-Json
$TOKEN = $resp.access_token

# Invia model_name malevolo
curl.exe -X POST http://localhost:8001/analyze/ `
  -H "Authorization: Bearer $TOKEN" `
  -F "file=@test_scan.nii.gz" `
  -F "model_name=http://169.254.169.254/latest/meta-data/"
```

### Risultato ottenuto
✅ HTTP 422 — `{"detail":"Modello non valido. Valori accettati: ['HC_vs_bvFTD', 'HC_vs_nfvPPA', 'HC_vs_svPPA']"}`  
Il valore non è nella whitelist e viene rifiutato immediatamente prima di qualsiasi
elaborazione o accesso al filesystem.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# orchestrator/routers/analyze.py
@router.post("/", response_model=dict)
async def upload_nifti_file(
    ...
    model_name: str = Form(...),
    ...
):
    # model_name usato direttamente senza validazione
    # poteva contenere URL, path traversal, injection
    new_task = Task(model_name=model_name, ...)
    background_tasks.add_task(run_full_pipeline, model_name=model_name)
```

**DOPO (codice sicuro):**
```python
# orchestrator/routers/analyze.py  (riga 20–29)
ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}

def _validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Modello non valido. Valori accettati: {sorted(ALLOWED_MODELS)}"
        )
    return model_name
```
```python
# model_service/main.py  (riga 17–25) — stessa whitelist applicata anche lato model_service
ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}

def _validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Modello non valido. Valori accettati: {sorted(ALLOWED_MODELS)}"
        )
    return model_name
```

**Perché funziona:**  
Il pattern whitelist è il contrario di una blacklist: anziché vietare i valori
pericolosi noti (impossibile da mantenere completa), si elencano esplicitamente
i soli valori accettati. Qualsiasi stringa non nell'insieme `ALLOWED_MODELS`
viene rifiutata con 422. La validazione viene applicata in doppio (orchestrator
e model_service) per difesa in profondità.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #6 — BFLA (endpoint admin senza controllo ruolo)
**OWASP:** API5 — Broken Function Level Authorization  
**File modificato:** `api_gateway/core/security.py` (riga 120–126) + `api_gateway/routers/auth.py` (riga 238–244) + `api_gateway/models/domain.py` (riga 7–9)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un utente normale (ruolo "user") è autenticato con un token JWT valido.
Tenta di accedere a `GET /admin/users` per ottenere la lista di tutti gli utenti
registrati nel sistema. Se l'endpoint non controlla il ruolo, qualsiasi utente
autenticato può eseguire operazioni privilegiate.

### Comando di test eseguito
```powershell
# Login come utente normale (non admin)
$resp = curl.exe -s -X POST http://localhost:8006/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=utente_normale&password=User1234!" | ConvertFrom-Json
$USER_TOKEN = $resp.access_token

# Tenta accesso all'endpoint admin
curl.exe -X GET http://localhost:8006/admin/users `
  -H "Authorization: Bearer $USER_TOKEN"
```

### Risultato ottenuto
✅ HTTP 403 — `{"detail":"Accesso negato: privilegi insufficienti"}`  
Il token JWT è valido (firma corretta, non scaduto) ma il ruolo dell'utente
non è "admin". La dependency `require_admin` blocca la richiesta prima
che il codice dell'endpoint venga eseguito.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/routers/auth.py
@router.get("/admin/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    # Nessun controllo di ruolo: qualsiasi utente autenticato accedeva
    current_user: User = Depends(get_current_user),
):
    return db.query(User).all()
```

**DOPO (codice sicuro):**
```python
# api_gateway/models/domain.py  (riga 7–9)
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
```
```python
# api_gateway/core/security.py  (riga 120–126)
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: privilegi insufficienti",
        )
    return current_user
```
```python
# api_gateway/routers/auth.py  (riga 238–244)
@router.get("/admin/users", response_model=list[UserResponse])
def list_users(
    admin: User = Depends(require_admin),   # <-- blocca non-admin con 403
    db: Session = Depends(get_db),
):
    return db.query(User).all()
```

**Perché funziona:**  
`require_admin` è una FastAPI Dependency che chiama internamente `get_current_user`
(verifica token) e poi controlla `current_user.role == "admin"`. Il valore del ruolo
è codificato nell'enum `UserRole` e nel JWT al momento del login; un utente
non può modificarlo senza accesso al database o alla chiave segreta. La dependency
viene valutata prima del corpo dell'endpoint, quindi il codice privilegiato
non viene mai raggiunto da utenti non autorizzati.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #7 — Riuso token dopo logout (Token Revocation)
**OWASP:** API2 — Broken Authentication  
**File modificato:** `api_gateway/core/security.py` (riga 87–93, 129–138) + `api_gateway/models/domain.py` (riga 27–33) + `api_gateway/routers/auth.py` (riga 166–180)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante ottiene un token JWT valido (intercettato, rubato o estratto da log).
La vittima effettua il logout. L'attaccante tenta di riutilizzare il token originale
per accedere alle API. Se il server non mantiene una blacklist dei token revocati,
il token rimane valido fino alla sua scadenza naturale (15 minuti) anche dopo il logout.

### Comando di test eseguito
```powershell
# 1. Login e recupero token
$resp = curl.exe -s -X POST http://localhost:8006/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=Admin1234!" | ConvertFrom-Json
$TOKEN = $resp.access_token

# 2. Logout (revoca il token)
curl.exe -X POST http://localhost:8006/logout `
  -H "Authorization: Bearer $TOKEN"

# 3. Tentativo di riuso del token revocato
curl.exe -X GET http://localhost:8001/analyze/ `
  -H "Authorization: Bearer $TOKEN"
```

### Risultato ottenuto
✅ HTTP 401 — `{"detail":"Token revocato. Effettua nuovamente il login."}`  
Il JWT è ancora crittograficamente valido (firma corretta, non scaduto) ma il suo
identificatore univoco (`jti`) è stato inserito nella blacklist al momento del logout.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/routers/auth.py — logout senza revoca
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    # Cancellava solo il cookie lato client — il token Bearer restava valido
    response.delete_cookie(key=_REFRESH_COOKIE)
```
```python
# api_gateway/core/security.py — nessuna blacklist
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = _decode_token(token)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user
```

**DOPO (codice sicuro):**
```python
# api_gateway/models/domain.py  (riga 27–33)
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```
```python
# api_gateway/core/security.py  (riga 87–93) — controllo blacklist
def _check_not_revoked(jti: str, db: Session) -> None:
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocato. Effettua nuovamente il login.",
            headers={"WWW-Authenticate": "Bearer"},
        )
```
```python
# api_gateway/core/security.py  (riga 129–138) — inserimento in blacklist
def revoke_token(token: str, db: Session) -> None:
    payload = _decode_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.commit()
```
```python
# api_gateway/routers/auth.py  (riga 166–180) — logout con revoca
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    token: str = Depends(_oauth2),
    refresh_token: Optional[str] = Cookie(default=None, alias=_REFRESH_COOKIE),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    revoke_token(token, db)
    if refresh_token:
        try:
            revoke_token(refresh_token, db)
        except Exception:
            pass
    response.delete_cookie(key=_REFRESH_COOKIE)
```

**Perché funziona:**  
Ogni token JWT contiene un campo `jti` (JWT ID), un UUID generato al momento della
creazione e incluso nel payload firmato. Al logout, il `jti` viene salvato nella
tabella `revoked_tokens` con la data di scadenza. Ad ogni richiesta successiva,
`get_current_user` chiama `_check_not_revoked` che fa una query al DB: se il `jti`
è in blacklist, risponde 401 indipendentemente dalla validità crittografica del token.
La colonna `expires_at` permette di ripulire periodicamente i token già scaduti
dalla blacklist senza compromettere la sicurezza.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #8 — Mass assignment (privilege escalation via role)
**OWASP:** API3 — Broken Object Property Level Authorization  
**File modificato:** `api_gateway/models/schemas.py` (riga 6–29, 32–36) + `api_gateway/routers/auth.py` (riga 75–94)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante tenta di registrarsi specificando nel payload JSON il campo `role: "admin"`.
Se il backend assegna i campi dell'input JSON direttamente all'oggetto database (mass
assignment), l'utente riesce a crearsi un account con privilegi elevati senza
passare dal controllo dell'amministratore.

### Comando di test eseguito
```powershell
curl.exe -X POST http://localhost:8006/register `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"hacker\",\"password\":\"Test1234!\",\"role\":\"admin\"}"
```

### Risultato ottenuto
✅ `{"id":5,"username":"hacker","role":"user"}` — Il campo `role` è ignorato.  
Il server crea l'account ma assegna sempre `role="user"`, indipendentemente
da quanto specificato nel payload. Nessuna escalation di privilegi avviene.

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/models/schemas.py — schema unico con role esponibile
class User(BaseModel):
    username: str
    password: str
    role: str = "user"   # Il client poteva inviare role="admin"
```
```python
# api_gateway/routers/auth.py — assegnazione diretta dall'input
@router.post("/register", ...)
def register(user: User, db: Session = Depends(get_db)):
    new_user = UserModel(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role,   # Pericoloso: il role veniva copiato dall'input
    )
```

**DOPO (codice sicuro):**
```python
# api_gateway/models/schemas.py  (riga 6–36)
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    # NESSUN campo 'role': il client non può specificarlo
    ...

class UserResponse(BaseModel):
    id: int
    username: str
    role: str   # Solo in output, mai in input
    model_config = ConfigDict(from_attributes=True)
```
```python
# api_gateway/routers/auth.py  (riga 75–94)
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/hour")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        email=user.email or None,
        role="user",   # Hardcoded: il role NON viene mai preso dall'input
    )
```

**Perché funziona:**  
I due schemi Pydantic separati (`UserCreate` per l'input, `UserResponse` per l'output)
sono il pattern fondamentale contro il mass assignment. Lo schema di input non espone
il campo `role`, quindi Pydantic lo ignora silenziosamente anche se presente nel JSON.
Il valore `role="user"` è hardcoded nel codice del router: nessun percorso di codice
legge `role` dall'input dell'utente durante la registrazione pubblica.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #9 — Security Headers mancanti
**OWASP:** API8 — Security Misconfiguration  
**File modificato:** `api_gateway/main.py` (riga 105–115) + `orchestrator/main.py` (riga 47–57) + `model_service/main.py` (riga 54–64)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante (o uno scanner automatico di sicurezza) ispeziona gli header HTTP
delle risposte del server. L'assenza di header come `X-Content-Type-Options`,
`X-Frame-Options` e `X-XSS-Protection` rende il client vulnerabile ad attacchi
di tipo MIME sniffing, clickjacking e XSS riflesso. L'header `Server` espone
la tecnologia usata (es. "uvicorn") facilitando fingerprinting e exploit mirati.

### Comando di test eseguito
```powershell
# Verifica header di sicurezza su api_gateway
curl.exe -I http://localhost:8006/

# Verifica header su orchestrator
curl.exe -I http://localhost:8001/

# Verifica header su model_service
curl.exe -I http://localhost:8003/
```

### Risultato ottenuto
✅ Header di sicurezza presenti in tutte e tre le risposte:
```
server: webserver
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
```
Il vero nome del server (uvicorn) è mascherato da "webserver".

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/main.py — nessun middleware per security headers
app = FastAPI(title="Clinical Twin — API Gateway", ...)
app.add_middleware(CORSMiddleware, ...)
app.include_router(auth.router)
# Risposte non contenevano alcun security header
# Header "server: uvicorn" esposto di default
```

**DOPO (codice sicuro):**
```python
# api_gateway/main.py  (riga 105–115)
# orchestrator/main.py  (riga 47–57)
# model_service/main.py (riga 54–64)  — stesso pattern nei tre servizi

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["server"] = "webserver"
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["x-xss-protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Perché funziona:**  
`BaseHTTPMiddleware` di Starlette intercetta ogni risposta HTTP prima che venga
inviata al client. Il middleware aggiunge gli header di sicurezza a tutte le risposte
indipendentemente dall'endpoint. I quattro header hanno ruoli distinti:
- `server: webserver` — nasconde il nome reale del server (uvicorn) prevenendo fingerprinting
- `x-content-type-options: nosniff` — impedisce al browser di fare MIME type sniffing
- `x-frame-options: DENY` — blocca il framing della pagina in iframe (anti-clickjacking)
- `x-xss-protection: 1; mode=block` — attiva il filtro XSS integrato nei browser legacy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEST #10 — JWT scadenza 15 minuti
**OWASP:** API2 — Broken Authentication  
**File modificato:** `api_gateway/core/config.py` (riga 11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Attacco simulato
Un attaccante intercetta un access token JWT (es. da log, proxy o rete non cifrata).
Se il token ha una lunga durata di vita (es. 24 ore o 30 giorni), l'attaccante
ha una finestra temporale molto ampia per abusarne. Ridurre la scadenza a 15 minuti
limita drasticamente il danno da token rubato.

### Comando di test eseguito
```powershell
# 1. Login e recupero token
$resp = curl.exe -s -X POST http://localhost:8006/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=Admin1234!" | ConvertFrom-Json

# 2. Verifica il campo expires_in nella risposta
Write-Host "expires_in:" $resp.expires_in

# 3. Decodifica il payload JWT (base64) per leggere exp e iat
$parts = $resp.access_token.Split('.')
$pad = $parts[1].Length % 4
if ($pad -ne 0) { $parts[1] += "=" * (4 - $pad) }
$payload = [System.Text.Encoding]::UTF8.GetString(
    [System.Convert]::FromBase64String($parts[1])
)
Write-Host "Payload JWT:" $payload
```

### Risultato ottenuto
✅ `expires_in: 900` — la risposta conferma 900 secondi (15 minuti esatti).  
Il payload decodificato del JWT mostra `"exp": <iat+900>` — differenza di 900 secondi
tra `iat` (issued at) e `exp` (expiration time).

### Modifica al codice applicata

**PRIMA (codice vulnerabile):**
```python
# api_gateway/core/config.py
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
# Token validi per 30 minuti: finestra di abuso doppia rispetto al necessario
```

**DOPO (codice sicuro):**
```python
# api_gateway/core/config.py  (riga 11)
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
```
```python
# api_gateway/routers/auth.py  (riga 120–121) — allineato alla configurazione
return {
    "access_token": access_token,
    "token_type": "bearer",
    "expires_in": 15 * 60,   # 900 secondi — comunicato esplicitamente al client
}
```

**Perché funziona:**  
Un token JWT è stateless: una volta emesso, il server non può invalidarlo prima
della scadenza (senza blacklist — vedi Test 7). Ridurre la finestra a 15 minuti
significa che un token rubato è utile solo per un tempo limitato. Il meccanismo
di refresh token (con scadenza 7 giorni, conservato in cookie HttpOnly) garantisce
che l'utente legittimo non debba riautenticarsi manualmente ogni 15 minuti.
I due meccanismi si complementano: JWT corto per sicurezza, refresh cookie per UX.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## RIEPILOGO MODIFICHE AI FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
┌──────────────────────────────────────────┬──────────────────────────────────────────────────┬────────────┐
│ File                                     │ Modifica applicata                               │ Test       │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/core/config.py               │ ACCESS_TOKEN_EXPIRE_MINUTES = 15                 │ T1, T10    │
│                                          │ Validator SECRET_KEY >= 64 caratteri             │ T1         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/core/security.py             │ _decode_token con try/except JWTError → 401      │ T1         │
│                                          │ _check_not_revoked: blacklist jti via DB         │ T7         │
│                                          │ get_current_user: aggiunto controllo jti         │ T7         │
│                                          │ require_admin: dependency ruolo admin            │ T6         │
│                                          │ revoke_token: inserisce jti in revoked_tokens    │ T7         │
│                                          │ _build_token: aggiunto campo jti (UUID)          │ T7         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/core/limiter.py              │ Creazione slowapi Limiter(key_func=IP)           │ T2         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/routers/auth.py              │ @limiter.limit("5/minute") su /login             │ T2         │
│                                          │ @limiter.limit("5/hour") su /register            │ T2         │
│                                          │ require_admin su /admin/users, /admin/users/{id} │ T6         │
│                                          │ revoke_token(token) + revoke_token(refresh) nel  │ T7         │
│                                          │ logout                                           │            │
│                                          │ role="user" hardcoded in /register               │ T8         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/models/schemas.py            │ UserCreate: @field_validator username (regex)    │ T4         │
│                                          │ UserCreate: @field_validator password (strength) │ T4         │
│                                          │ Schema separato UserCreate / UserResponse        │ T8         │
│                                          │ UserResponse: nessun campo password/hashed_pwd  │ T8         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/models/domain.py             │ Enum UserRole (user / admin)                     │ T6         │
│                                          │ Tabella RevokedToken (jti, revoked_at, expires)  │ T7         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ api_gateway/main.py                      │ SecurityHeadersMiddleware (4 header)             │ T9         │
│                                          │ docs/redoc/openapi disabilitati in produzione    │ T9         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ orchestrator/routers/analyze.py          │ ALLOWED_MODELS whitelist + _validate_model_name  │ T5         │
│                                          │ Filtro Task.owner_id == current_user.id su       │ T3         │
│                                          │ get_task_status, get_medico_tasks, get_nifti     │            │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ orchestrator/main.py                     │ SecurityHeadersMiddleware (4 header)             │ T9         │
│                                          │ docs/redoc/openapi disabilitati in produzione    │ T9         │
├──────────────────────────────────────────┼──────────────────────────────────────────────────┼────────────┤
│ model_service/main.py                    │ ALLOWED_MODELS whitelist + _validate_model_name  │ T5         │
│                                          │ SecurityHeadersMiddleware (4 header)             │ T9         │
│                                          │ docs/redoc/openapi disabilitati in produzione    │ T9         │
└──────────────────────────────────────────┴──────────────────────────────────────────────────┴────────────┘
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TABELLA TEST FINALI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
┌──────┬───────────────────────┬──────────┬──────────────────────────────────┬────────┐
│ Test │ Attacco               │ OWASP    │ Atteso                           │ Esito  │
├──────┼───────────────────────┼──────────┼──────────────────────────────────┼────────┤
│ T1   │ Token falso (JWT)     │ API2     │ HTTP 401 — firma non valida      │ ✅     │
│ T2   │ Brute force login     │ API4     │ HTTP 429 al 6° tentativo         │ ✅     │
│ T3   │ BOLA task altrui      │ API1     │ HTTP 404 — owner_id mismatch     │ ✅     │
│ T4   │ XSS nel username      │ API3     │ HTTP 422 — regex whitelist       │ ✅     │
│ T5   │ SSRF via model_name   │ API7     │ HTTP 422 — ALLOWED_MODELS        │ ✅     │
│ T6   │ BFLA endpoint admin   │ API5     │ HTTP 403 — ruolo insufficiente   │ ✅     │
│ T7   │ Riuso token post-     │ API2     │ HTTP 401 — jti in blacklist      │ ✅     │
│      │ logout                │          │                                  │        │
│ T8   │ Mass assignment role  │ API3     │ role="user" (ignorato admin)     │ ✅     │
│ T9   │ Security headers      │ API8     │ 4 header presenti in risposta    │ ✅     │
│ T10  │ JWT scadenza 15 min   │ API2     │ expires_in=900 secondi           │ ✅     │
└──────┴───────────────────────┴──────────┴──────────────────────────────────┴────────┘
```

**10/10 test superati.**  
Tutti eseguiti manualmente dal terminale tramite `curl.exe` su Windows PowerShell.  
Servizi testati in esecuzione locale su Docker Compose (porte 8006, 8001, 8003).

---

*Documento generato il 23 Giugno 2026 — Clinical Twin v2.0.0*
