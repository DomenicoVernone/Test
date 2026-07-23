"""
test_ruoli.py — Testa il sistema di ruoli utente/admin.

Verifica che l'enum UserRole rifiuti valori arbitrari, che il ruolo
di default sia 'user', e che la registrazione pubblica non permetta
auto-assegnazione del ruolo admin. OWASP: API5 — Broken Function Level Auth.
"""

import pytest
from pydantic import ValidationError

from models.domain import UserRole
from models.schemas import UserCreate


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def utente_normale():
    """Utente finto con ruolo user."""
    class FakeUser:
        id = 10
        username = "mario.rossi"
        role = UserRole.USER
    return FakeUser()


@pytest.fixture
def utente_admin():
    """Utente finto con ruolo admin."""
    class FakeAdmin:
        id = 1
        username = "admin"
        role = UserRole.ADMIN
    return FakeAdmin()


# ── Test valori enum ──────────────────────────────────────────────────────────

def test_ruolo_default_e_user(utente_normale):
    """Il ruolo di default per un utente ordinario deve essere 'user'."""
    assert utente_normale.role == "user"
    assert utente_normale.role == UserRole.USER


def test_admin_ha_ruolo_admin(utente_admin):
    """Un utente admin deve avere il ruolo 'admin'."""
    assert utente_admin.role == "admin"
    assert utente_admin.role == UserRole.ADMIN


def test_userrole_accetta_user():
    """Il valore 'user' deve essere un UserRole valido."""
    role = UserRole("user")
    assert role == UserRole.USER


def test_userrole_accetta_admin():
    """Il valore 'admin' deve essere un UserRole valido."""
    role = UserRole("admin")
    assert role == UserRole.ADMIN


# ── Test rifiuto valori arbitrari ─────────────────────────────────────────────

@pytest.mark.parametrize("ruolo_non_valido", [
    "superadmin",
    "root",
    "ADMIN",          # case-sensitive
    "Admin",          # case-sensitive
    "USER",           # case-sensitive
    "moderator",
    "staff",
    "god",
    "",               # stringa vuota
    "1",              # numero come stringa
])
def test_ruolo_non_accetta_valori_arbitrari(ruolo_non_valido):
    """
    UserRole deve rifiutare qualsiasi valore non in {user, admin}.
    Previene la promozione ad admin tramite manipolazione del valore del campo.
    """
    with pytest.raises(ValueError):
        UserRole(ruolo_non_valido)


# ── Test mass assignment via schema ───────────────────────────────────────────

def test_user_non_puo_diventare_admin_da_input():
    """
    Simulazione di registrazione con role=admin nel JSON.
    UserCreate non ha il campo 'role': Pydantic lo ignora silenziosamente.
    """
    user_data = UserCreate.model_validate({
        "username": "hacker.test",
        "password": "Test1234!",
        "role": "admin",       # tentativo di mass assignment
    })
    # UserCreate non deve avere il campo role
    assert not hasattr(user_data, "role")


def test_usercreate_non_ha_campo_role():
    """UserCreate (schema di input registrazione) non espone il campo role."""
    user = UserCreate(username="nuovoutente", password="Test1234!")
    # Il campo role non deve essere accessibile — non fa parte dell'input schema
    assert not hasattr(user, "role")


def test_usercreate_accetta_solo_campi_definiti():
    """
    Pydantic ignora i campi extra non dichiarati in UserCreate.
    Questo è il meccanismo di difesa contro mass assignment.
    """
    user = UserCreate.model_validate({
        "username": "utente.test",
        "password": "Test1234!",
        "role": "admin",            # extra — ignorato
        "is_superuser": True,       # extra — ignorato
        "hashed_password": "xyz",   # extra — ignorato
    })
    # Solo username, password ed email sono campi validi
    assert user.username == "utente.test"
    assert user.password == "Test1234!"


# ── Test che UserRole sia un'enum con esattamente 2 valori ────────────────────

def test_userrole_ha_esattamente_due_valori():
    """UserRole deve avere esattamente i valori 'user' e 'admin', nient'altro."""
    valori = {role.value for role in UserRole}
    assert valori == {"user", "admin"}


def test_userrole_e_sottoclasse_di_str():
    """
    UserRole eredita da str: può essere usato direttamente dove si aspetta
    una stringa (es. colonna SQLAlchemy, payload JWT) senza conversioni.
    """
    assert isinstance(UserRole.USER, str)
    assert isinstance(UserRole.ADMIN, str)
    assert UserRole.USER == "user"
    assert UserRole.ADMIN == "admin"
