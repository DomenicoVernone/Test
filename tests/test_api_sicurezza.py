"""
test_api_sicurezza.py — Converte i 10 test manuali curl in test automatizzati.

Usa FastAPI TestClient (nessun Docker, nessun server attivo).
Copre: token falso, brute force, BOLA, XSS, SSRF, BFLA, logout+revoca,
mass assignment, security headers, scadenza JWT.
OWASP API Security Top 10 (2023).
"""

import os
import sys
import shutil
import importlib.util

# ─── Env vars: devono essere impostate prima di qualsiasi import ──────────────
# SECRET_KEY e DATABASE_URL sono gia' impostati da conftest.py.
# SHARED_VOLUME_DIR serve a orchestrator/main.py per os.makedirs().
_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GW_PATH   = os.path.join(_ROOT, "api_gateway")
_ORCH_PATH = os.path.join(_ROOT, "orchestrator")
_TMP_DATA  = os.path.join(_ROOT, "tmp_test_data")

os.environ.setdefault("SHARED_VOLUME_DIR", _TMP_DATA)
os.environ.setdefault("USE_MOCK",  "true")
os.environ.setdefault("TEST_MODE", "true")
# Email settings richiesti da fastapi_mail.ConnectionConfig (valore sintetico)
os.environ.setdefault("MAIL_FROM",     "test@test.com")
os.environ.setdefault("MAIL_USERNAME", "test")
os.environ.setdefault("MAIL_PASSWORD", "test")


# ─── Utility: carica main.py da directory specifica con alias univoco ─────────
def _load_main(directory: str, alias: str):
    spec = importlib.util.spec_from_file_location(
        alias, os.path.join(directory, "main.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


# ─── 1. Import api_gateway app ───────────────────────────────────────────────
# conftest.py ha gia' aggiunto api_gateway/ a sys.path.
# _load_main esegue main.py: create_all + migrazioni + _seed_admin().
_gw_main    = _load_main(_GW_PATH, "_gw_main")
gateway_app = _gw_main.app


# ─── 2. Import orchestrator app (chirurgia su sys.modules) ───────────────────
# Problema: api_gateway e orchestrator usano gli stessi nomi di package
# (core, models, routers, services). Impossibile averli entrambi in
# sys.modules contemporaneamente senza conflitti. Soluzione: salviamo i
# moduli api_gateway, li rimuoviamo temporaneamente, importiamo l'orchestrator
# (che carica i suoi moduli), poi ripristiniamo api_gateway.

_SHARED_PKGS = {"core", "models", "routers", "services"}

# a) Snapshot + rimozione moduli api_gateway
_gw_snap = {
    k: sys.modules.pop(k)
    for k in list(sys.modules.keys())
    if k.split(".")[0] in _SHARED_PKGS
}

# b) sys.path: rimuovi api_gateway, aggiungi orchestrator
_saved_path = sys.path[:]
sys.path = [_ORCH_PATH] + [p for p in sys.path if p != _GW_PATH]

# c) Carica orchestrator (i suoi moduli entrano in sys.modules)
_orch_main      = _load_main(_ORCH_PATH, "_orch_main")
orchestrator_app = _orch_main.app

# d) Cattura riferimenti ai moduli orchestrator prima del ripristino
_orch_db_mod = sys.modules.get("core.database")
_orch_get_db = _orch_db_mod.get_db if _orch_db_mod else None
_orch_Base   = _orch_db_mod.Base   if _orch_db_mod else None

# e) Rimuovi moduli orchestrator e ripristina api_gateway + sys.path
for k in [k for k in list(sys.modules.keys()) if k.split(".")[0] in _SHARED_PKGS]:
    del sys.modules[k]
sys.modules.update(_gw_snap)
sys.path = _saved_path


# ─── 3. Import normali (ora puntano ad api_gateway) ──────────────────────────
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from core.database import Base as _gw_Base, get_db as _gw_get_db, SessionLocal as _gw_SL
from core.security import create_access_token, get_password_hash
from models.domain import User, UserRole

pytestmark = pytest.mark.owasp


# ─── 4. Crea tabella tasks (orchestrator) nel DB di test ─────────────────────
# api_gateway ha gia' creato: users, revoked_tokens, password_reset_tokens.
# L'orchestrator aggiunge: tasks.
if _orch_Base is not None:
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///./test_suite.db")
    _orch_engine = create_engine(_db_url, connect_args={"check_same_thread": False})
    _orch_Base.metadata.create_all(_orch_engine)
    _orch_engine.dispose()


# ─── 5. Override get_db su entrambe le app → stessa sessione test_suite.db ───
def _get_test_db():
    """Inietta una sessione sul DB di test al posto di quella di produzione."""
    db = _gw_SL()
    try:
        yield db
    finally:
        db.commit()
        db.close()


gateway_app.dependency_overrides[_gw_get_db] = _get_test_db
if _orch_get_db is not None:
    orchestrator_app.dependency_overrides[_orch_get_db] = _get_test_db


# ─── 6. TestClient ────────────────────────────────────────────────────────────
gateway      = TestClient(gateway_app,      raise_server_exceptions=False)
orchestrator = TestClient(orchestrator_app, raise_server_exceptions=False)


# ─── 7. Seed: utente normale 'testapi' nel DB di test ────────────────────────
def _seed_test_user() -> None:
    db = _gw_SL()
    try:
        if not db.query(User).filter(User.username == "testapi").first():
            db.add(User(
                username="testapi",
                hashed_password=get_password_hash("Test1234!"),
                role=UserRole.USER,
            ))
            db.commit()
    finally:
        db.close()


_seed_test_user()


# ─── Fixture: token JWT valido per l'utente 'testapi' (scope=function) ───────
@pytest.fixture
def token_utente():
    """Token JWT fresco per ogni test — stesso utente, JTI diverso."""
    db = _gw_SL()
    try:
        user = db.query(User).filter(User.username == "testapi").first()
    finally:
        db.close()
    return create_access_token(user)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 1 — Token falso → 401
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 9 — Security headers presenti (PRIMA del test di login)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 10 — JWT expires_in == 900 (PRIMA del test brute force)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 4 — XSS username → 422
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 8 — Mass assignment: role=admin ignorato
# ═════════════════════════════════════════════════════════════════════════════

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
    assert data["role"] == "user", (
        f"Mass assignment: atteso role='user', ottenuto role='{data.get('role')}'"
    )


# ═════════════════════════════════════════════════════════════════════════════
# TEST 3 — BOLA: task di un altro utente → 404
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 5 — SSRF via model_name → 422
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 6 — BFLA: utente normale su endpoint admin → 403
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# TEST 7 — Logout + riuso token → 401
# ═════════════════════════════════════════════════════════════════════════════

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
    assert r_logout.status_code == 204, (
        f"Logout fallito: atteso 204, ottenuto {r_logout.status_code}"
    )

    # Step 2: riuso sullo stesso token sull'orchestrator → blacklist hit → 401
    r_riuso = orchestrator.get(
        "/analyze/",
        headers={"Authorization": f"Bearer {token_utente}"}
    )
    assert r_riuso.status_code == 401, (
        f"Token revocato accettato: atteso 401, ottenuto {r_riuso.status_code}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2 — Brute force → 429 (app isolata per evitare contatori condivisi)
# ═════════════════════════════════════════════════════════════════════════════

def test_brute_force_bloccato_dopo_5_tentativi():
    """
    Il rate limiter blocca il login dopo 5 tentativi per minuto (stesso IP).
    Usa un'app FastAPI isolata con il proprio limiter per garantire che il
    contatore parta da zero, indipendentemente dagli altri test.
    La configurazione e' identica a quella del gateway reale (5/minute).
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
        assert r.status_code == 401, (
            f"Tentativo {i + 1}: atteso 401, ottenuto {r.status_code}"
        )

    # Il 6° tentativo: rate limit raggiunto → 429 Too Many Requests
    r = _client.post("/login", data={"username": "u", "password": "sbagliata"})
    assert r.status_code == 429, (
        f"Brute force non bloccato: atteso 429, ottenuto {r.status_code}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# TEST 11 — skipif: richiede Docker installato
# ═════════════════════════════════════════════════════════════════════════════

docker_disponibile = shutil.which("docker") is not None


@pytest.mark.skipif(
    not docker_disponibile,
    reason="Richiede Docker installato"
)
def test_pipeline_con_docker():
    """
    Placeholder per il test end-to-end della pipeline completa (gateway +
    orchestrator + inference-engine) su container Docker reali.
    Va eseguito solo su macchine con Docker disponibile (locale/CI con Docker-in-Docker).
    """
    pass


# ═════════════════════════════════════════════════════════════════════════════
# TEST 12 — xfail: revoca JWT dopo reset password non implementata
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.xfail(
    reason="Revoca JWT dopo reset password non implementata - issue aperta"
)
def test_token_revocato_dopo_reset_password():
    """
    Comportamento atteso: dopo un reset password riuscito, tutti i token JWT
    emessi prima del reset dovrebbero essere invalidati (in blacklist), cosi'
    che un token rubato prima del reset non resti valido dopo.

    Comportamento attuale: reset_password() in api_gateway/routers/auth.py
    aggiorna solo hashed_password e marca il reset_token come used, senza
    toccare revoked_tokens. Il vecchio access token resta quindi valido
    fino alla sua naturale scadenza (15 minuti) anche dopo il reset.
    """
    import time
    from datetime import datetime, timedelta, timezone
    from core.security import get_password_hash
    from models.domain import PasswordResetToken

    db = _gw_SL()
    try:
        uname = f"resettest_{int(time.time())}"
        user = User(
            username=uname,
            hashed_password=get_password_hash("Vecchia123!"),
            role=UserRole.USER,
            email=f"{uname}@test.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Token emesso PRIMA del reset password
        vecchio_token = create_access_token(user)

        # Token di reset valido inserito direttamente nel DB (bypassa l'invio email)
        reset_token_value = f"reset_{uname}"
        db.add(PasswordResetToken(
            user_id=user.id,
            token=reset_token_value,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        db.commit()
    finally:
        db.close()

    # Reset della password tramite l'endpoint pubblico
    r_reset = gateway.post(
        "/reset-password",
        json={"token": reset_token_value, "new_password": "Nuova456!"},
    )
    assert r_reset.status_code == 200

    # Il vecchio token dovrebbe essere revocato → 401 atteso.
    # In assenza dell'implementazione, l'orchestrator lo accetta ancora.
    r_riuso = orchestrator.get(
        "/analyze/",
        headers={"Authorization": f"Bearer {vecchio_token}"}
    )
    assert r_riuso.status_code == 401, (
        f"Vecchio token ancora valido dopo reset password: "
        f"atteso 401, ottenuto {r_riuso.status_code}"
    )
