"""
conftest.py — Fixtures condivise e configurazione di base per pytest.

Questo file viene eseguito da pytest PRIMA di qualsiasi test.
Imposta le variabili d'ambiente necessarie e aggiunge i path di
importazione affinché i moduli api_gateway siano visibili.
"""

import os
import sys

# ── Impostazione env vars PRIMA di qualsiasi import che usi settings ──────────
# SECRET_KEY >= 64 caratteri è obbligatorio (validatore in core/config.py)
os.environ.setdefault("SECRET_KEY", "a" * 64)
# DATABASE_URL: punta a un file temporaneo (non al volume Docker condiviso)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_suite.db")
# Email: valori sintetici per fastapi_mail.ConnectionConfig (non invia realmente email)
os.environ.setdefault("MAIL_FROM",     "test@test.com")
os.environ.setdefault("MAIL_USERNAME", "test")
os.environ.setdefault("MAIL_PASSWORD", "test")

# ── Aggiunge api_gateway al sys.path per gli import ──────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GATEWAY_PATH = os.path.join(_ROOT, "api_gateway")

if _GATEWAY_PATH not in sys.path:
    sys.path.insert(0, _GATEWAY_PATH)

# ── Import delle dipendenze (dopo aver impostato env vars) ────────────────────
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import get_password_hash
from models.domain import User, UserRole


# ── Fixture: database SQLite isolato in tmp_path ──────────────────────────────

@pytest.fixture
def db_session(tmp_path):
    """
    Database SQLite temporaneo e isolato per ogni test.
    Crea tutte le tabelle, poi le elimina dopo il test.
    """
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_con_utente(tmp_path):
    """
    Database SQLite temporaneo con un utente 'testuser' / 'Test1234!' già inserito.
    Usato dai test di autenticazione.
    """
    db_file = tmp_path / "test_auth.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    utente = User(
        username="testuser",
        hashed_password=get_password_hash("Test1234!"),
        role=UserRole.USER,
    )
    db.add(utente)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


# ── Fixture: utente finto (senza DB) ─────────────────────────────────────────

@pytest.fixture
def utente_test():
    """
    Oggetto User finto per testare la generazione di token JWT
    senza toccare il database.
    """
    class FakeUser:
        id = 42
        username = "dottore.test"
        role = "user"

    return FakeUser()


@pytest.fixture
def utente_admin():
    """Utente finto con ruolo admin."""
    class FakeAdmin:
        id = 1
        username = "admin"
        role = UserRole.ADMIN

    return FakeAdmin()


@pytest.fixture
def utente_normale():
    """Utente finto con ruolo user."""
    class FakeUser:
        id = 99
        username = "mario.rossi"
        role = UserRole.USER

    return FakeUser()
