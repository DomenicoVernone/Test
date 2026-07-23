"""
test_validazione_input.py — Testa la validazione degli input utente.

Verifica che i validatori Pydantic su UserCreate accettino valori
corretti e rifiutino valori pericolosi (XSS, SQL injection, troppo
corti/lunghi). OWASP: API3 — Broken Object Property Level Authorization.
"""

import pytest
from pydantic import ValidationError

from models.schemas import UserCreate, ResetPasswordRequest

pytestmark = pytest.mark.validazione


# ── Usernames validi ────────────────────────────────────────────────────────

@pytest.mark.parametrize("username", [
    "mario.rossi",
    "dottore_1",
    "user-test",
    "abc",
    "A1b",
    "nome.cognome.123",
])
def test_username_valido_accettato(username):
    """Usernames che rispettano il pattern [a-zA-Z0-9_.-]{3,50} devono essere accettati."""
    user = UserCreate(username=username, password="Test1234!")
    assert user.username == username


# ── Usernames non validi ─────────────────────────────────────────────────────

@pytest.mark.parametrize("username", [
    "<script>alert(1)</script>",   # XSS: caratteri < > non permessi
    "a",                            # troppo corto (min 3 caratteri)
    "a" * 51,                       # troppo lungo (max 50 caratteri)
    "user name",                    # spazio non permesso
    "user@name",                    # @ non permessa
    "'; DROP TABLE users;--",       # SQL injection: caratteri speciali
    "",                             # stringa vuota
    "ab",                           # 2 caratteri: sotto il minimo
    "user/path",                    # slash non permesso
    "user<admin>",                  # angolari non permesse
])
def test_username_non_valido_rifiutato(username):
    """Usernames con caratteri pericolosi o fuori range devono sollevare ValueError."""
    with pytest.raises((ValueError, ValidationError)):
        UserCreate(username=username, password="Test1234!")


# ── Password valide ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("password", [
    "Test1234!",      # classica: maiuscola + numero + speciale
    "Password1",      # minimo: maiuscola + numero + 8 caratteri
    "Abcdefg1",       # esattamente 8 caratteri con maiuscola e numero
    "SuperSecure99",  # lunga e sicura
    "Admin2026",      # contiene Admin + anno
])
def test_password_valida_accettata(password):
    """Password che soddisfano tutti i requisiti devono essere accettate."""
    user = UserCreate(username="utente.ok", password=password)
    assert user.password == password


# ── Password non valide ───────────────────────────────────────────────────────

@pytest.mark.parametrize("password", [
    "abc",           # troppo corta (< 8 caratteri)
    "password",      # no maiuscola, no numero
    "password1",     # no maiuscola (tutto minuscolo + cifra)
    "testtest",      # no numero, no maiuscola
    "12345678",      # solo numeri — no maiuscola
    "Abcdefgh",      # maiuscola presente ma no numero
    "Test123",       # 7 caratteri — sotto il minimo
])
def test_password_non_valida_rifiutata(password):
    """Password che non soddisfano i requisiti devono sollevare ValueError."""
    with pytest.raises((ValueError, ValidationError)):
        UserCreate(username="utente.ok", password=password)


# ── Validazione password anche in ResetPasswordRequest ───────────────────────

@pytest.mark.parametrize("password", [
    "Test1234!",
    "Nuova9876",
])
def test_reset_password_valida_accettata(password):
    """Le stesse regole di complessità si applicano al reset della password."""
    req = ResetPasswordRequest(token="tok_abc123", new_password=password)
    assert req.new_password == password


@pytest.mark.parametrize("password", [
    "corta",         # troppo corta
    "nessunanum",    # no numero no maiuscola
])
def test_reset_password_debole_rifiutata(password):
    """Password deboli rifiutate anche nel reset."""
    with pytest.raises((ValueError, ValidationError)):
        ResetPasswordRequest(token="tok_abc123", new_password=password)


# ── Mass assignment: il campo role è ignorato ─────────────────────────────────

def test_role_ignorato_in_registrazione():
    """
    UserCreate non ha il campo 'role': Pydantic lo ignora silenziosamente.
    Un attaccante non può auto-assegnarsi il ruolo admin via JSON.
    """
    user = UserCreate.model_validate({
        "username": "hacker.test",
        "password": "Test1234!",
        "role": "admin",       # campo extra — deve essere ignorato
        "is_superuser": True,  # campo extra — deve essere ignorato
    })
    assert not hasattr(user, "role")
    assert not hasattr(user, "is_superuser")
    assert user.username == "hacker.test"
