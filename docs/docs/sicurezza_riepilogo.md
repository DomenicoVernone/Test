# Riepilogo Sicurezza API — Clinical Twin
**Progetto:** Tesi-FTD — MLOps Clinical Twin  
**Standard:** OWASP API Security Top 10 (2023)  
**Data:** 2026-06-23

---

## Introduzione

Questa documentazione di sicurezza è organizzata in tre file. Il file **Modifiche al codice** (`sicurezza_modifiche_codice.md`) descrive in dettaglio le 30 modifiche implementate, suddivise in 6 gruppi tematici (autenticazione JWT, autorizzazione, validazione input, protezione risorse, configurazione, funzionalità sicure aggiunte): ogni modifica include il codice prima e dopo il fix, la spiegazione dell'attacco che previene e l'impatto concreto. Il file **Test eseguiti** (`sicurezza_test.md`) raccoglie i 10 test manuali eseguiti con PowerShell per verificare che le protezioni funzionino effettivamente a runtime, con comandi pronti all'uso, output atteso e risultato ottenuto. Questo file di riepilogo offre una visione d'insieme rapida: la tabella delle 30 modifiche, il security score OWASP per categoria e le due misure non ancora implementate.

---

## Tabella riepilogo finale delle 30 modifiche

| #  | Modifica                                          | File principale                           | OWASP  |
|----|---------------------------------------------------|-------------------------------------------|--------|
| 1  | Scadenza access token 15 minuti                   | `api_gateway/core/config.py:11`           | API2   |
| 2  | Refresh token in cookie httpOnly + SameSite       | `api_gateway/routers/auth.py:38-47`       | API2   |
| 3  | Blacklist JTI al logout (revoca token)            | `api_gateway/core/security.py:87-138`     | API2   |
| 4  | SECRET_KEY >= 64 caratteri (validator)            | `api_gateway/core/config.py:24-31`        | API2   |
| 5  | `sub` JWT = user_id numerico (RFC 7519)           | `api_gateway/core/security.py:62-66`      | API2   |
| 6  | bcrypt rounds=12 espliciti (auditabile)           | `api_gateway/core/security.py:17-21`      | API2   |
| 7  | Timing attack protection (dummy hash)             | `api_gateway/core/security.py:28,39-48`   | API2   |
| 8  | Password strength validation (8+/upper/digit)     | `api_gateway/models/schemas.py:20-29`     | API2   |
| 9  | BOLA: owner_id su ogni query task                 | `orchestrator/routers/analyze.py:120-178` | API1   |
| 10 | BFLA: enum UserRole user/admin                    | `api_gateway/models/domain.py:7-23`       | API5   |
| 11 | `require_admin` dependency centralizzata          | `api_gateway/core/security.py:120-126`    | API5   |
| 12 | Endpoint `/admin/*` segregati                     | `auth.py:238-258`, `analyze.py:192-203`   | API5   |
| 13 | Mass assignment: schema input/output separati     | `api_gateway/models/schemas.py:6-54`      | API3   |
| 14 | Whitelist model_name — no SSRF/path traversal     | `orchestrator/routers/analyze.py:20-29`   | API7   |
| 15 | Username regex whitelist — blocco XSS             | `api_gateway/models/schemas.py:11-18`     | API3   |
| 16 | Validazione NIfTI con magic bytes                 | `orchestrator/routers/analyze.py:32-66`   | API3   |
| 17 | Rate limiting login: 5/minuto                     | `api_gateway/routers/auth.py:100`         | API4   |
| 18 | Rate limiting register: 3/min (admin), 5/h (pub)  | `api_gateway/routers/auth.py:53,76`       | API4   |
| 19 | Rate limiting pipeline analisi: 3/minuto          | `orchestrator/routers/analyze.py:70`      | API4   |
| 20 | Rate limiting forgot-password: 3/ora              | `api_gateway/routers/auth.py:186`         | API4   |
| 21 | Security headers HTTP su tutti i microservizi     | `*/main.py:SecurityHeadersMiddleware`     | API8   |
| 22 | Docs Swagger/OpenAPI nascosti in produzione       | `api_gateway/main.py:90-98`               | API9   |
| 23 | Porte microservizi su loopback 127.0.0.1          | `docker-compose.yml:27,46,65,88,109`      | API8   |
| 24 | Errori R non esposti al client (generico)         | `model_service/main.py:75-83`             | API8   |
| 25 | Fallback MLflow con errore generico               | `model_service/main.py:86-94`             | API10  |
| 26 | Registrazione pubblica `/register` — ruolo fisso  | `api_gateway/routers/auth.py:75-94`       | API5   |
| 27 | `/forgot-password` — risposta 200 sempre          | `api_gateway/routers/auth.py:185-205`     | API2   |
| 28 | `/reset-password` — token usa-e-getta + scadenza  | `api_gateway/routers/auth.py:208-233`     | API2   |
| 29 | Credenziali SMTP da variabili d'ambiente (.env)   | `api_gateway/services/email.py`           | API8   |
| 30 | Invalidazione token reset precedenti (rotation)   | `api_gateway/routers/auth.py:193-200`     | API2   |

---

## Security score OWASP finale

| OWASP | Categoria                              | Score | Note |
|-------|----------------------------------------|-------|------|
| API1  | Broken Object Level Authorization      | ✅    | BOLA con `owner_id` su tutte le query task (#9) |
| API2  | Broken Authentication                  | ✅    | 8 modifiche: JWT 15min, httpOnly cookie, blacklist JTI, bcrypt 12, timing, password strength, forgot/reset sicuri (#1–8, #27–28, #30) |
| API3  | Broken Object Property Level Auth      | ✅    | Schema separati, regex username, magic bytes NIfTI (#13, #15, #16) |
| API4  | Unrestricted Resource Consumption      | ✅    | Rate limiting su login, register, pipeline, forgot-password (#17–20) |
| API5  | Broken Function Level Authorization    | ✅    | Enum ruoli, require_admin, endpoint /admin/* segregati, register sicuro (#10–12, #26) |
| API6  | Unrestricted Access to Sensitive Flows | ⚠️    | Rate limiting presente; manca autenticazione nativa sull'inference engine R (accesso solo via rete interna Docker) |
| API7  | Server Side Request Forgery            | ✅    | Whitelist model_name su orchestrator E model_service (#14) |
| API8  | Security Misconfiguration              | ✅    | Security headers, docs nascosti, loopback binding, errori generici, credenziali da env (#21–24, #29) |
| API9  | Improper Inventory Management          | ✅    | Docs Swagger/OpenAPI disabilitati in produzione (#22) |
| API10 | Unsafe Consumption of APIs             | ✅    | Fallback MLflow con errore generico e logging interno (#25) |

**Legenda:**
- ✅ Coperto con misure efficaci e verificate nel codice
- ⚠️ Parzialmente coperto — presente ma con margini di miglioramento
- ❌ Non coperto

**Score complessivo: 9/10 categorie coperte (API6 parziale)**

---

## Modifiche non implementate

Le seguenti misure erano indicate nella specifica di progetto ma **non sono implementate** nel codice analizzato:

### 1. Revoca JWT dopo reset password

**Stato:** ❌ Non implementato  
**Dove manca:** `api_gateway/routers/auth.py:208-233` (funzione `reset_password`)  
**Problema:** Dopo un reset password, i JWT di sessione attivi NON vengono revocati. Un attaccante che ha già un access token valido (rubato prima del reset) può continuare a usarlo per i restanti 15 minuti.  
**Fix raccomandato:** Aggiungere un campo `password_changed_at` al modello `User` e verificare nella `get_current_user()` che il JWT sia stato emesso dopo quel timestamp. In alternativa, revocare tutti i JWT attivi dell'utente inserendo i JTI nella blacklist al momento del reset.

```python
# Da aggiungere in reset_password() dopo user.hashed_password = ...
user.password_changed_at = datetime.now(timezone.utc)
db.commit()

# Da aggiungere in get_current_user() dopo il decode del token:
if user.password_changed_at:
    token_iat = datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc)
    if token_iat < user.password_changed_at:
        raise HTTPException(status_code=401, detail="Token non valido dopo cambio password")
```

### 2. Blocco client-side 60 secondi dopo tentativi falliti

**Stato:** ⚠️ Non verificabile dal codice backend  
**Dove dovrebbe essere:** Codice frontend React (non analizzato)  
**Nota:** Questa logica risiede nel frontend e non è verificabile dall'analisi del codice backend. Si ricorda che il blocco client-side è **solo UX** — può essere aggirato da qualsiasi strumento che non sia il browser. Il rate limiting server-side (#17) è la vera protezione ed è implementato correttamente.

---

---

## Test automatizzati Pytest

Oltre all'analisi statica e ai 10 test manuali, la codebase è coperta da una suite di test automatizzati:

> **131 test Pytest organizzati in 7 file — tutti PASSED**  
> Comando: `python -m pytest tests/ -v`  
> File: `tests/test_api_sicurezza.py`, `test_validazione_input.py`, `test_sicurezza_jwt.py`, `test_model_name.py`, `test_ruoli.py`, `test_autenticazione.py`, `test_file_mri.py`

I test verificano (senza Docker): integrazione HTTP end-to-end via TestClient, validazione input, token JWT, whitelist model_name, sistema dei ruoli, timing attack protection e magic bytes NIfTI. Per i dettagli vedere `sicurezza_test.md` — sezione *Test automatizzati con Pytest*.

---

*Riepilogo generato il 2026-06-23 — Analisi statica su 13 file sorgente*  
*Suite Pytest aggiornata il 2026-07-08 — 131 test (incl. 10 TestClient), tutti PASSED*  
*Standard: OWASP API Security Top 10 (2023 Edition)*
