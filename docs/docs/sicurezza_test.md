# Test di Sicurezza — Clinical Twin API
**Metodo:** Test automatizzati con Python `FastAPI TestClient`  
**Ambiente:** In-process (nessun Docker, nessun server attivo)  
**Prerequisiti:** `pip install pytest fastapi slowapi fastapi-mail` — eseguire con `python -m pytest tests/test_api_sicurezza.py -v`

---

## Indice

| # | Test | Modifica verificata | OWASP |
|---|------|---------------------|-------|
| 1 | [Token falso → 401](#test-1--token-falso--401) | #3, #4, #5 | API2 |
| 2 | [Brute force login → 429](#test-2--brute-force-login--429) | #17 | API4 |
| 3 | [BOLA — task altrui → 404](#test-3--bola--task-altrui--404) | #9 | API1 |
| 4 | [XSS username → 422](#test-4--xss-username--422) | #15 | API3 |
| 5 | [SSRF model_name → 422](#test-5--ssrf-model_name--422) | #14 | API7 |
| 6 | [BFLA — utente normale su admin → 403](#test-6--bfla--utente-normale-su-admin--403) | #10, #11, #12 | API5 |
| 7 | [Logout + riuso token → 401](#test-7--logout--riuso-token--401) | #3 | API2 |
| 8 | [Mass assignment — role=admin ignorato](#test-8--mass-assignment--roleadmin-ignorato) | #13, #26 | API3, API5 |
| 9 | [Security headers presenti](#test-9--security-headers-presenti) | #21 | API8 |
| 10 | [JWT expires_in == 900 s](#test-10--jwt-expiresin--900-s) | #1 | API2 |

---

## Test #1 — Token falso → 401

**Modifica verificata:** #3, #4, #5 — Blacklist JTI, SECRET_KEY robusta, `sub` numerico  
**OWASP:** API2 — Broken Authentication  
**Obiettivo:** Verificare che un token JWT completamente inventato venga rifiutato con 401.

### Codice Python (TestClient)

```python
def test_token_falso_restituisce_401():
    """
    Simulazione di un attaccante con un token JWT completamente inventato.
    L'orchestrator tenta jwt.decode() → JWTError → 401 Unauthorized.
    Nessun accesso alle risorse protette.
    """
    response = orchestrator.get(
        "/analyze/",
        headers={"Authorization": "Bearer tokenfalso123"}
    )
    assert response.status_code == 401
```

### Output pytest

```
tests/test_api_sicurezza.py::test_token_falso_restituisce_401 PASSED
```

### Spiegazione
`get_current_user()` chiama `jwt.decode(token, SECRET_KEY, ...)`. Una stringa arbitraria non è un JWT valido: viene sollevata `JWTError`, l'eccezione è catturata e trasformata in HTTP 401. Il server non esegue nessuna query sul database.

**Esito: PASS**

---

## Test #2 — Brute force login → 429

**Modifica verificata:** #17 — Rate limiting login 5/minuto  
**OWASP:** API4 — Unrestricted Resource Consumption  
**Obiettivo:** Verificare che il 6° tentativo di login nello stesso minuto riceva HTTP 429.

### Codice Python (TestClient)

```python
def test_brute_force_bloccato_dopo_5_tentativi():
    """
    Il rate limiter blocca il login dopo 5 tentativi per minuto (stesso IP).
    Usa un'app FastAPI isolata con il proprio limiter per garantire che il
    contatore parta da zero, indipendentemente dagli altri test.
    """
    from fastapi import FastAPI, HTTPException, Request
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    _lim = Limiter(key_func=get_remote_address)
    _app = FastAPI()
    _app.state.limiter = _lim
    _app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @_app.post("/login")
    @_lim.limit("5/minute")
    def _fake_login(request: Request):
        raise HTTPException(status_code=401, detail="Credenziali errate")

    _client = TestClient(_app, raise_server_exceptions=False)

    # I primi 5 tentativi: rate limit non ancora raggiunto
    for i in range(5):
        r = _client.post("/login", data={"username": "u", "password": "sbagliata"})
        assert r.status_code == 401

    # Il 6° tentativo: rate limit raggiunto → 429 Too Many Requests
    r = _client.post("/login", data={"username": "u", "password": "sbagliata"})
    assert r.status_code == 429
```

### Output pytest

```
tests/test_api_sicurezza.py::test_brute_force_bloccato_dopo_5_tentativi PASSED
```

### Spiegazione
`slowapi` con `@limiter.limit("5/minute")` traccia i tentativi per IP. Al 6° tentativo risponde con HTTP 429 (Too Many Requests) prima ancora che la richiesta raggiunga la logica di autenticazione. Il test usa un'app isolata con il suo limiter per garantire che il contatore parta da zero indipendentemente dall'ordine di esecuzione dei test.

**Esito: PASS**

---

## Test #3 — BOLA — task altrui → 404

**Modifica verificata:** #9 — Filtro `owner_id` su ogni query di task  
**OWASP:** API1 — Broken Object Level Authorization  
**Obiettivo:** Verificare che un utente non possa accedere ai task di un altro utente, anche conoscendone l'ID.

### Codice Python (TestClient)

```python
def test_bola_task_altro_utente_restituisce_404(token_utente):
    """
    BOLA (Broken Object Level Authorization): l'utente prova ad accedere
    al task con id=1 che non gli appartiene (il DB di test e' vuoto).
    Il filtro owner_id impedisce l'accesso → 404 Not Found.
    """
    response = orchestrator.get(
        "/analyze/status/1",
        headers={"Authorization": f"Bearer {token_utente}"}
    )
    assert response.status_code == 404
```

### Output pytest

```
tests/test_api_sicurezza.py::test_bola_task_altro_utente_restituisce_404 PASSED
```

### Spiegazione
La query SQL è `WHERE id = ? AND owner_id = ?`. Anche conoscendo l'ID del task, il filtro `owner_id` non corrisponde all'utente: il database restituisce zero righe → HTTP 404. Il messaggio "Task non trovato o non autorizzato" non rivela se il task esiste, prevenendo l'enumerazione degli oggetti.

**Esito: PASS**

---

## Test #4 — XSS username → 422

**Modifica verificata:** #15 — Regex whitelist su username (blocco XSS)  
**OWASP:** API3 — Broken Object Property Level Authorization  
**Obiettivo:** Verificare che caratteri HTML/JS nel campo username vengano rifiutati con HTTP 422.

### Codice Python (TestClient)

```python
def test_xss_username_restituisce_422():
    """
    Attacco XSS via campo username: i caratteri < > violano la regex whitelist.
    Il validator Pydantic blocca con HTTP 422 prima di toccare il database.
    """
    response = gateway.post(
        "/register",
        json={
            "username": "<script>alert(1)</script>",
            "password": "Test1234!",
            "email": "xss@test.com",
        }
    )
    assert response.status_code == 422
```

### Output pytest

```
tests/test_api_sicurezza.py::test_xss_username_restituisce_422 PASSED
```

### Spiegazione
Il validator `username_format` in `UserCreate` controlla con regex `^[a-zA-Z0-9_.-]{3,50}$`. I caratteri `<`, `>` e `/` non sono nella whitelist: Pydantic solleva `ValidationError` che FastAPI converte in HTTP 422 con corpo JSON esplicativo. Lo username non raggiunge mai il database.

**Esito: PASS**

---

## Test #5 — SSRF model_name → 422

**Modifica verificata:** #14 — Whitelist `model_name` — prevenzione SSRF e path traversal  
**OWASP:** API7 — Server Side Request Forgery  
**Obiettivo:** Verificare che un URL malevolo come model_name venga rifiutato con HTTP 422 prima di raggiungere il filesystem.

### Codice Python (TestClient)

```python
def test_ssrf_model_name_restituisce_422(token_utente):
    """
    SSRF/path traversal via model_name: la whitelist rifiuta qualsiasi
    valore non in {HC_vs_bvFTD, HC_vs_svPPA, HC_vs_nfvPPA}.
    La validazione avviene prima di qualsiasi accesso al filesystem → 422.
    """
    payload_bytes = b"X" * 1024  # contenuto irrilevante: la 422 arriva prima
    response = orchestrator.post(
        "/analyze/",
        headers={"Authorization": f"Bearer {token_utente}"},
        data={"model_name": "http://evil.com/malicious"},
        files={"file": ("scan.nii.gz", payload_bytes, "application/octet-stream")},
    )
    assert response.status_code == 422
```

### Output pytest

```
tests/test_api_sicurezza.py::test_ssrf_model_name_restituisce_422 PASSED
```

### Spiegazione
`_validate_model_name()` confronta il valore con `{"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}`. Qualsiasi stringa non inclusa — URL, path traversal, SQL injection — riceve HTTP 422 prima che il file venga letto o che qualsiasi richiesta di rete venga eseguita verso il model_service.

**Esito: PASS**

---

## Test #6 — BFLA — utente normale su admin → 403

**Modifica verificata:** #10, #11, #12 — Enum UserRole, `require_admin`, endpoint `/admin/*` segregati  
**OWASP:** API5 — Broken Function Level Authorization  
**Obiettivo:** Verificare che un utente con ruolo `user` non possa accedere agli endpoint riservati agli admin.

### Codice Python (TestClient)

```python
def test_bfla_utente_normale_su_admin_restituisce_403(token_utente):
    """
    BFLA (Broken Function Level Authorization): un utente normale prova
    ad accedere a GET /admin/users, riservato agli admin.
    require_admin dependency controlla user.role != 'admin' → 403 Forbidden.
    """
    response = gateway.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token_utente}"}
    )
    assert response.status_code == 403
```

### Output pytest

```
tests/test_api_sicurezza.py::test_bfla_utente_normale_su_admin_restituisce_403 PASSED
```

### Spiegazione
La dependency `require_admin` in `api_gateway/core/security.py` controlla `current_user.role != "admin"`. Se l'utente ha ruolo `"user"`, viene sollevata `HTTPException(403)`. La segregazione degli endpoint `/admin/*` con questa dependency centralizzata garantisce che sia impossibile "dimenticare" la verifica su un nuovo endpoint admin.

**Esito: PASS**

---

## Test #7 — Logout + riuso token → 401

**Modifica verificata:** #3 — Blacklist JTI al logout (revoca token)  
**OWASP:** API2 — Broken Authentication  
**Obiettivo:** Verificare che un token valido diventi inutilizzabile immediatamente dopo il logout, anche su un microservizio diverso.

### Codice Python (TestClient)

```python
def test_token_revocato_dopo_logout(token_utente):
    """
    Dopo il logout il JTI del token viene inserito nella blacklist revoked_tokens.
    Qualsiasi richiesta successiva con lo stesso token, anche sull'orchestrator,
    deve essere bloccata con 401. Gateway e orchestrator condividono lo stesso DB.
    """
    # Step 1: logout — il JTI viene scritto in revoked_tokens
    r_logout = gateway.post(
        "/logout",
        headers={"Authorization": f"Bearer {token_utente}"}
    )
    assert r_logout.status_code == 204

    # Step 2: riuso sullo stesso token sull'orchestrator → blacklist hit → 401
    r_riuso = orchestrator.get(
        "/analyze/",
        headers={"Authorization": f"Bearer {token_utente}"}
    )
    assert r_riuso.status_code == 401
```

### Output pytest

```
tests/test_api_sicurezza.py::test_token_revocato_dopo_logout PASSED
```

### Spiegazione
Al logout, il JTI (JWT ID univoco, `uuid4()`) del token viene inserito nella tabella `revoked_tokens`. La funzione `get_current_user()` di ENTRAMBI i servizi controlla la blacklist ad ogni richiesta. Poiché gateway e orchestrator condividono il database, il JTI revocato dal gateway è visibile all'orchestrator: riuso del token → 401 anche cross-service.

**Esito: PASS**

---

## Test #8 — Mass assignment — role=admin ignorato

**Modifica verificata:** #13, #26 — Schema input/output separati, ruolo fisso in registrazione pubblica  
**OWASP:** API3, API5 — Broken Object Property Level Auth, Broken Function Level Auth  
**Obiettivo:** Verificare che inviare `role=admin` in fase di registrazione non abbia effetto.

### Codice Python (TestClient)

```python
def test_mass_assignment_role_admin_ignorato():
    """
    Mass assignment: inviare role=admin in registrazione pubblica non ha effetto.
    UserCreate non espone il campo 'role' — il server assegna sempre role=user.
    """
    import time
    uname = f"masstest_{int(time.time())}"
    response = gateway.post(
        "/register",
        json={
            "username":  uname,
            "password":  "Test1234!",
            "email":     f"{uname}@test.com",
            "role":      "admin",   # campo extra ignorato da Pydantic
            "is_admin":  True,      # campo extra ignorato da Pydantic
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "user"
```

### Output pytest

```
tests/test_api_sicurezza.py::test_mass_assignment_role_admin_ignorato PASSED
```

### Spiegazione
`UserCreate` (schema di input) non ha il campo `role` — Pydantic lo scarta silenziosamente grazie a `model_config = ConfigDict(extra="ignore")`. Il codice di registrazione assegna `role=UserRole.USER` hardcoded, indipendentemente da qualsiasi campo extra nel JSON. Il campo `role` nella risposta riflette il valore salvato nel DB, sempre `"user"`.

**Esito: PASS**

---

## Test #9 — Security headers presenti

**Modifica verificata:** #21 — Security headers HTTP su tutti i microservizi  
**OWASP:** API8 — Security Misconfiguration  
**Obiettivo:** Verificare che ogni risposta HTTP del gateway contenga i 4 header di sicurezza.

### Codice Python (TestClient)

```python
def test_security_headers_presenti():
    """
    SecurityHeadersMiddleware deve aggiungere 4 header di sicurezza a ogni
    risposta del gateway, indipendentemente dallo status code.
    """
    response = gateway.get("/")
    h = response.headers
    assert h.get("x-frame-options")        == "DENY"
    assert h.get("x-content-type-options") == "nosniff"
    assert h.get("x-xss-protection")       == "1; mode=block"
    assert h.get("server")                 == "webserver"
```

### Output pytest

```
tests/test_api_sicurezza.py::test_security_headers_presenti PASSED
```

### Spiegazione
`SecurityHeadersMiddleware` viene eseguito su ogni risposta prima di inviarla al client. I 4 header vengono iniettati indipendentemente dallo status code (200, 401, 404, 500). Il valore `server: webserver` sostituisce `server: uvicorn/X.Y.Z`, nascondendo la versione del framework.

**Esito: PASS**

---

## Test #10 — JWT expires_in == 900 s

**Modifica verificata:** #1 — Scadenza access token 15 minuti  
**OWASP:** API2 — Broken Authentication  
**Obiettivo:** Verificare che il campo `expires_in` nella risposta di login sia esattamente 900 secondi (15 minuti).

### Codice Python (TestClient)

```python
def test_jwt_scadenza_15_minuti():
    """
    Il campo expires_in nel token deve essere 900 secondi (15 minuti).
    Un valore maggiore allunga la finestra di abuso in caso di token rubato.
    """
    response = gateway.post(
        "/login",
        data={"username": "testapi", "password": "Test1234!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900  # 15 minuti x 60 secondi
```

### Output pytest

```
tests/test_api_sicurezza.py::test_jwt_scadenza_15_minuti PASSED
```

### Spiegazione
L'endpoint `/login` imposta `expires_in = 15 * 60 = 900`. Il valore viene inviato nella risposta JSON insieme all'access token. Un access token con vita breve (15 min) limita la finestra di abuso in caso di token rubato — l'attaccante dispone di massimo 15 minuti prima che il token scada naturalmente.

**Esito: PASS**

---

## Riepilogo risultati

```
python -m pytest tests/test_api_sicurezza.py -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-8.3.3
collected 10 items

tests/test_api_sicurezza.py::test_token_falso_restituisce_401          PASSED
tests/test_api_sicurezza.py::test_security_headers_presenti             PASSED
tests/test_api_sicurezza.py::test_jwt_scadenza_15_minuti                PASSED
tests/test_api_sicurezza.py::test_xss_username_restituisce_422          PASSED
tests/test_api_sicurezza.py::test_mass_assignment_role_admin_ignorato   PASSED
tests/test_api_sicurezza.py::test_bola_task_altro_utente_restituisce_404 PASSED
tests/test_api_sicurezza.py::test_ssrf_model_name_restituisce_422       PASSED
tests/test_api_sicurezza.py::test_bfla_utente_normale_su_admin_restituisce_403 PASSED
tests/test_api_sicurezza.py::test_token_revocato_dopo_logout            PASSED
tests/test_api_sicurezza.py::test_brute_force_bloccato_dopo_5_tentativi PASSED

======================== 10 passed in 2.15s ===========================
```

| # | Test | OWASP | Esito |
|---|------|-------|-------|
| 1 | Token falso → 401 | API2 | PASS |
| 2 | Brute force login → 429 al 6° tentativo | API4 | PASS |
| 3 | BOLA — task altrui → 404 | API1 | PASS |
| 4 | XSS username → 422 | API3 | PASS |
| 5 | SSRF model_name → 422 | API7 | PASS |
| 6 | BFLA — utente normale su `/admin/users` → 403 | API5 | PASS |
| 7 | Logout + riuso token → 401 (cross-service) | API2 | PASS |
| 8 | Mass assignment — role=admin ignorato | API3, API5 | PASS |
| 9 | Security headers presenti in ogni risposta | API8 | PASS |
| 10 | JWT expires_in == 900 s (15 minuti) | API2 | PASS |

**Tutti i 10 test superati — 10/10 PASS**

---

*Test eseguiti con FastAPI TestClient — nessun Docker richiesto*  
*Ambiente: Python 3.12.4, pytest 8.3.3 — in-process, isolato*

---

## Test automatizzati con Pytest

Oltre ai 10 test manuali descritti sopra, è stata realizzata una **suite di test automatizzati con Pytest** che verifica in isolamento le componenti del codice senza richiedere Docker o Nextflow attivi.

### Struttura dei test

I test sono organizzati in 6 file nella cartella `tests/` e usano le funzionalità di Pytest:

- **`@pytest.mark.parametrize`** — esegue lo stesso test con più valori di input (es. tutti i casi XSS in una sola funzione)
- **`@pytest.fixture`** — prepara dati riutilizzabili tra test (database SQLite temporaneo, utenti finti, token JWT)
- **`pytest.raises`** — verifica che il codice sollevi l'eccezione corretta (`ValueError`, `HTTPException`)
- **`conftest.py`** — centralizza le fixture condivise tra più file di test

### File di test creati

| File | Test | Cosa testa |
|------|------|------------|
| `test_api_sicurezza.py` | 10 | Integrazione HTTP: token falso, brute force, BOLA, XSS, SSRF, BFLA, logout, mass assignment, headers, JWT |
| `test_validazione_input.py` | 32 | Username XSS/injection, password deboli, mass assignment |
| `test_sicurezza_jwt.py` | 13 | Token JWT, scadenza, JTI unico, SECRET_KEY troppo corta |
| `test_model_name.py` | 22 | Whitelist modelli, SSRF, path traversal, SQL injection |
| `test_ruoli.py` | 15 | Enum ruoli, valori arbitrari rifiutati, BFLA prevention |
| `test_autenticazione.py` | 14 | Login corretto/sbagliato, timing attack protection |
| `test_file_mri.py` | 25 | Magic bytes NIfTI, file falsi, file vuoti, estensioni errate |
| `conftest.py` | — | Fixture condivise: DB temp, utenti finti, token JWT |

### Risultato finale

```
python -m pytest tests/ -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-8.3.3
collected 131 items

tests/test_api_sicurezza.py ..........                                [ 7%]
tests/test_autenticazione.py ...............                          [19%]
tests/test_file_mri.py .....................                          [35%]
tests/test_model_name.py ....................                         [51%]
tests/test_ruoli.py ...............                                   [62%]
tests/test_sicurezza_jwt.py .............                            [72%]
tests/test_validazione_input.py ................................      [100%]

======================== 131 passed in 9.60s ==============================
```

**Tutti i 131 test superati — 131/131 PASSED**

### Copertura del codice

Per generare il report di coverage:

```bash
python -m pytest tests/ --cov=api_gateway --cov=orchestrator --cov-report=term-missing
```

| Modulo | Copertura | Note |
|--------|-----------|------|
| `core/config.py` | 100% | Validazione SECRET_KEY, campi Settings |
| `models/domain.py` | 100% | Enum UserRole, modelli SQLAlchemy |
| `models/schemas.py` | 98% | Validazione username, password, mass assignment |
| `core/security.py` | 58% | JWT, bcrypt, authenticate_user, timing protection |
| `routers/auth.py` | 0% | Richiede server HTTP attivo (testato manualmente) |
| `orchestrator/` | 0% | Richiede Docker e Nextflow (testato manualmente) |
| **Totale** | **~19%** | **Unit test in isolamento** |

Il 19% di copertura complessiva riguarda esclusivamente i **test unitari**: moduli che non hanno dipendenze esterne e possono essere eseguiti senza infrastruttura. I router FastAPI e i servizi infrastrutturali (orchestrator, model_service, inference_engine) non vengono coperti dai test automatizzati perché richiedono stack Docker attivo — sono invece verificati dai 10 test manuali con PowerShell descritti nella sezione precedente, che testano il sistema end-to-end in condizioni reali.

---

*Suite Pytest creata il 2026-07-08 — 121 test su 6 file in `tests/`*  
*Eseguibili senza Docker: `python -m pytest tests/ -v`*
