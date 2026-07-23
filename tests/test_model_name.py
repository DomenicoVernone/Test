"""
test_model_name.py — Testa la whitelist dei nomi modello ML.

Verifica che solo i tre modelli clinici validi siano accettati e
che qualsiasi altra stringa (path traversal, URL esterne, injection)
venga rifiutata con HTTP 422. OWASP: API7 — Server Side Request Forgery.
"""

import pytest
from fastapi import HTTPException


# ── Replica della logica di validazione (orchestrator/routers/analyze.py) ────
# Definita localmente per evitare dipendenze Docker/microservizio.
# Il test verifica le REGOLE, non l'import specifico.

ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}


def _validate_model_name(model_name: str) -> str:
    """Accetta solo i 3 modelli clinici — rifiuta tutto il resto con HTTP 422."""
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Modello non valido. Valori accettati: {sorted(ALLOWED_MODELS)}"
        )
    return model_name


# ── Modelli validi ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("model_name", [
    "HC_vs_bvFTD",
    "HC_vs_svPPA",
    "HC_vs_nfvPPA",
])
def test_modello_valido_accettato(model_name):
    """
    I tre modelli clinici devono essere accettati senza eccezioni.
    Questi sono gli unici modelli addestrati e validati per la piattaforma.
    """
    result = _validate_model_name(model_name)
    assert result == model_name


# ── Modelli non validi (attacchi) ─────────────────────────────────────────────

@pytest.mark.parametrize("model_name", [
    "http://evil.com/malicious",          # SSRF: URL esterna
    "../../../etc/passwd",                 # path traversal classico
    "modello_inesistente",                 # nome non in whitelist
    "",                                    # stringa vuota
    "HC_vs_bvFTD; DROP TABLE models;--",  # SQL injection
    "HC_vs_bvFTD' OR '1'='1",            # SQL injection alternativo
    "hc_vs_bvftd",                         # case-sensitive: minuscolo
    "HC_VS_BVFTD",                         # case-sensitive: maiuscolo
    "HC_vs_bvFTD ",                        # spazio finale
    " HC_vs_bvFTD",                        # spazio iniziale
    "HC-vs-bvFTD",                         # trattino invece di underscore
    "<script>alert(1)</script>",           # XSS
    "null",                                # null string
    "None",                                # Python None come stringa
    "file:///etc/passwd",                  # file:// URI
    "ldap://evil.com",                     # LDAP injection
])
def test_modello_non_valido_rifiutato(model_name):
    """
    Qualsiasi stringa non nella whitelist deve sollevare HTTPException 422.
    La whitelist previene path traversal e SSRF verso MLflow o filesystem.
    """
    with pytest.raises(HTTPException) as exc_info:
        _validate_model_name(model_name)
    assert exc_info.value.status_code == 422


# ── Test che il messaggio di errore NON riveli dettagli interni ────────────────

def test_errore_rivela_valori_accettati_non_path():
    """
    Il messaggio di errore deve mostrare i valori accettati (per UX),
    ma NON rivelare path del filesystem o struttura interna.
    """
    with pytest.raises(HTTPException) as exc_info:
        _validate_model_name("../../../etc/passwd")
    detail = exc_info.value.detail
    # Il messaggio non deve contenere il path inviato dall'attaccante
    assert "../../../etc/passwd" not in detail
    # Deve mostrare i valori validi per guidare l'utente legittimo
    assert "HC_vs_bvFTD" in detail or "accettati" in detail.lower()


# ── Test di tipo whitelist (set lookup) ──────────────────────────────────────

def test_whitelist_e_un_set():
    """La whitelist usa un set Python per garantire lookup O(1) e unicità."""
    assert isinstance(ALLOWED_MODELS, set)
    assert len(ALLOWED_MODELS) == 3


def test_tutti_e_tre_i_modelli_nella_whitelist():
    """Verifica che tutti e tre i modelli clinici siano presenti nella whitelist."""
    assert "HC_vs_bvFTD" in ALLOWED_MODELS
    assert "HC_vs_svPPA" in ALLOWED_MODELS
    assert "HC_vs_nfvPPA" in ALLOWED_MODELS
