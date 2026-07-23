"""
test_sicurezza_jwt.py — Testa la creazione e verifica dei token JWT.

Verifica che i token contengano i campi obbligatori (sub numerico,
exp, jti) e che le impostazioni di sicurezza (SECRET_KEY robusta)
siano applicate correttamente. OWASP: API2 — Broken Authentication.
"""

import pytest
from pydantic import ValidationError
from jose import jwt

from core.config import settings, Settings
from core.security import create_access_token, create_refresh_token

pytestmark = pytest.mark.jwt


# ── Fixture utente finto ──────────────────────────────────────────────────────

@pytest.fixture
def utente_test():
    """Utente finto riutilizzabile — non tocca il database."""
    class FakeUser:
        id = 42
        username = "dottore.test"
        role = "user"
    return FakeUser()


# ── Test struttura del token ───────────────────────────────────────────────────

def test_token_contiene_user_id_numerico(utente_test):
    """
    Il campo 'sub' del JWT deve essere il numeric ID dell'utente (RFC 7519).
    Questo impedisce ambiguità rispetto all'username, che è mutabile.
    """
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"].isdigit(), "sub deve essere un numero intero come stringa"
    assert payload["sub"] == str(utente_test.id)


def test_token_contiene_scadenza(utente_test):
    """
    Il JWT deve contenere il campo 'exp' per limitare la finestra di abuso
    in caso di furto del token (finestra di 15 minuti).
    """
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in payload, "exp (expiration) obbligatorio nel payload"


def test_token_contiene_jti(utente_test):
    """
    Il JWT deve contenere 'jti' (JWT ID) — identificatore unico usato
    dalla blacklist per revocare i token al logout.
    """
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "jti" in payload, "jti obbligatorio per supporto alla blacklist"
    assert len(payload["jti"]) > 0


def test_token_contiene_username(utente_test):
    """Il payload deve contenere il campo username per la UI del frontend."""
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["username"] == utente_test.username


def test_token_contiene_ruolo(utente_test):
    """Il payload deve contenere il campo role per i controlli di autorizzazione."""
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "role" in payload


# ── Test unicità JTI ──────────────────────────────────────────────────────────

def test_due_token_hanno_jti_diversi(utente_test):
    """
    Ogni token deve avere un JTI unico (UUID v4).
    Se due token avessero lo stesso JTI, revocare uno revocherebbe anche l'altro.
    """
    token1 = create_access_token(utente_test)
    token2 = create_access_token(utente_test)

    payload1 = jwt.decode(token1, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    payload2 = jwt.decode(token2, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload1["jti"] != payload2["jti"], "ogni token deve avere JTI distinto"


def test_refresh_token_ha_type_refresh(utente_test):
    """
    Il refresh token deve contenere 'type: refresh' per distinguerlo
    dall'access token e impedirne l'uso intercambiabile.
    """
    token = create_refresh_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("type") == "refresh"


def test_access_token_non_ha_type_refresh(utente_test):
    """L'access token non deve avere type=refresh — non può essere usato per /refresh."""
    token = create_access_token(utente_test)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("type") != "refresh"


# ── Test validazione SECRET_KEY ───────────────────────────────────────────────

def test_secret_key_corta_blocca_avvio():
    """
    Settings deve rifiutare chiavi più corte di 64 caratteri.
    Una chiave corta è vulnerabile a brute-force JWT.
    """
    with pytest.raises((ValueError, ValidationError)):
        Settings(SECRET_KEY="chiave_corta_non_sicura")  # 26 caratteri — troppo corta


def test_secret_key_esatta_64_caratteri_accettata():
    """Una SECRET_KEY di esattamente 64 caratteri deve essere accettata."""
    chiave_ok = "b" * 64
    s = Settings(SECRET_KEY=chiave_ok)
    assert s.SECRET_KEY == chiave_ok


def test_secret_key_lunga_accettata():
    """Una SECRET_KEY lunga (128 caratteri) deve essere accettata senza errori."""
    chiave_lunga = "c" * 128
    s = Settings(SECRET_KEY=chiave_lunga)
    assert len(s.SECRET_KEY) == 128


# ── Test scadenza access token ────────────────────────────────────────────────

def test_access_token_expire_default_15_minuti():
    """
    Il tempo di scadenza default dell'access token deve essere 15 minuti.
    Un valore più lungo (es. 24h) aumenta la finestra di abuso in caso di furto.
    """
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15


def test_refresh_token_expire_default_7_giorni():
    """Il refresh token ha una durata di 7 giorni — valore di default."""
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
