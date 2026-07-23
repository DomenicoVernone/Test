"""
test_autenticazione.py — Testa authenticate_user e la protezione timing.

Verifica che il login funzioni con credenziali corrette, rifiuti quelle
sbagliate, e che il tempo di risposta sia costante (protezione contro
timing attack / user enumeration). OWASP: API2 — Broken Authentication.
"""

import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import authenticate_user, get_password_hash
from models.domain import User, UserRole


# ── Fixture: database temporaneo con un utente ────────────────────────────────

@pytest.fixture
def db_con_utente(tmp_path):
    """
    Database SQLite isolato in tmp_path con l'utente 'testuser' / 'Test1234!'.
    Ogni test ottiene il suo database indipendente — nessuna interferenza.
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


# ── Test login corretto ───────────────────────────────────────────────────────

def test_login_corretto_restituisce_utente(db_con_utente):
    """
    Con credenziali corrette, authenticate_user deve restituire l'oggetto User.
    """
    user = authenticate_user("testuser", "Test1234!", db_con_utente)
    assert user is not None
    assert user.username == "testuser"


def test_login_corretto_restituisce_utente_con_id(db_con_utente):
    """L'utente restituito deve avere un ID intero positivo (chiave primaria DB)."""
    user = authenticate_user("testuser", "Test1234!", db_con_utente)
    assert user is not None
    assert isinstance(user.id, int)
    assert user.id > 0


def test_login_corretto_ruolo_user(db_con_utente):
    """L'utente creato tramite registrazione ha il ruolo 'user' di default."""
    user = authenticate_user("testuser", "Test1234!", db_con_utente)
    assert user is not None
    assert user.role == "user"


# ── Test login con credenziali sbagliate ─────────────────────────────────────

def test_password_sbagliata_restituisce_none(db_con_utente):
    """
    Una password errata deve restituire None, non sollevare eccezioni.
    Il chiamante (endpoint /login) gestisce il None con HTTP 401.
    """
    user = authenticate_user("testuser", "password_sbagliata", db_con_utente)
    assert user is None


def test_password_vuota_restituisce_none(db_con_utente):
    """Una password vuota non deve autenticare nessun utente."""
    user = authenticate_user("testuser", "", db_con_utente)
    assert user is None


@pytest.mark.parametrize("password_errata", [
    "Test1234",    # manca l'esclamativo finale
    "test1234!",   # minuscola invece di maiuscola
    "TEST1234!",   # tutto maiuscolo
    " Test1234!",  # spazio iniziale
    "Test1234! ",  # spazio finale
])
def test_varianti_password_sbagliata_restituisce_none(db_con_utente, password_errata):
    """Piccole variazioni della password corretta devono fallire l'autenticazione."""
    user = authenticate_user("testuser", password_errata, db_con_utente)
    assert user is None


# ── Test utente inesistente ───────────────────────────────────────────────────

def test_utente_inesistente_restituisce_none(db_con_utente):
    """
    Un username non presente nel DB deve restituire None (non un'eccezione).
    Il comportamento è identico a una password sbagliata — nessun leak.
    """
    user = authenticate_user("nonexiste", "Test1234!", db_con_utente)
    assert user is None


def test_utente_vuoto_restituisce_none(db_con_utente):
    """Username vuoto non deve autenticare nessuno."""
    user = authenticate_user("", "Test1234!", db_con_utente)
    assert user is None


# ── Test protezione timing attack ────────────────────────────────────────────

def test_timing_utente_esistente_vs_inesistente(db_con_utente):
    """
    Protezione timing: il tempo di risposta deve essere simile per
    'utente esistente + password sbagliata' e 'utente inesistente'.

    Senza la protezione (dummy hash), 'utente inesistente' sarebbe
    istantaneo (nessun bcrypt), rivelando quali username esistono.
    Con _DUMMY_HASH, entrambi eseguono verify_password() → tempo costante.

    Soglia: < 100ms di differenza.
    """
    # Warmup: la prima chiamata bcrypt può essere più lenta
    authenticate_user("testuser", "warmup", db_con_utente)
    authenticate_user("nonexiste", "warmup", db_con_utente)

    # Misura: utente esistente, password sbagliata (bcrypt su hash reale)
    start = time.perf_counter()
    authenticate_user("testuser", "password_sbagliata", db_con_utente)
    tempo_esistente = time.perf_counter() - start

    # Misura: utente inesistente (bcrypt su _DUMMY_HASH)
    start = time.perf_counter()
    authenticate_user("utente_che_non_esiste", "password_sbagliata", db_con_utente)
    tempo_inesistente = time.perf_counter() - start

    # I due tempi devono essere comparabili — entrambi eseguono bcrypt
    differenza = abs(tempo_esistente - tempo_inesistente)
    assert differenza < 0.1, (
        f"Timing attack possibile: differenza {differenza:.3f}s > 100ms. "
        f"esistente={tempo_esistente:.3f}s, inesistente={tempo_inesistente:.3f}s"
    )


# ── Test isolamento tra sessioni di test ──────────────────────────────────────

def test_database_isolato_tra_test(tmp_path):
    """
    Ogni fixture db_con_utente usa tmp_path separato: i test sono indipendenti.
    Crea un secondo DB senza utenti e verifica che 'testuser' non esista.
    """
    db_file = tmp_path / "altro_db.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # In questo DB non c'è nessun utente
    user = authenticate_user("testuser", "Test1234!", db)
    assert user is None

    db.close()
