# orchestrator/models/schemas.py
#
# Schemi Pydantic per la validazione dei dati in ingresso e in uscita.
# Separati dai modelli ORM per evitare di esporre dettagli del database
# nelle risposte HTTP (es. hashed_password non compare mai nelle response).

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    filename: str
    model_name: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    filename: str
    status: str
    progress: float
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    model_config = ConfigDict(from_attributes=True)