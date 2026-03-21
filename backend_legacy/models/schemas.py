# File: backend/models/schemas.py
"""
Modulo degli Schemi Pydantic.
Gestisce la validazione dei dati in ingresso (Richieste) e in uscita (Risposte) delle API.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# ==========================================
# SCHEMI UTENTE E AUTENTICAZIONE
# ==========================================

class UserCreate(BaseModel):
    """Schema per la registrazione di un nuovo Medico."""
    username: str
    password: str

class UserResponse(BaseModel):
    """Schema per la restituzione dei dati utente (Esclude tassativamente la password)."""
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Schema per il payload del Token JWT."""
    access_token: str
    token_type: str


# ==========================================
# SCHEMI TASK (Orchestrazione Asincrona)
# ==========================================

class TaskCreate(BaseModel):
    """Schema per l'inizializzazione di un nuovo Task di analisi."""
    filename: str
    model_name: Optional[str] = None

class TaskResponse(BaseModel):
    """
    Schema per la risposta di stato del Task.
    Cruciale per il polling asincrono del frontend React.
    """
    id: int
    filename: str
    status: str
    progress: float
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)