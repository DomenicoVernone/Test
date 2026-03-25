# api_gateway/core/config.py
#
# Configurazione centralizzata del servizio tramite pydantic-settings.
# Le variabili vengono lette dal file .env — vedere .env.example in root.

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Percorso del database SQLite — il volume /shared_db è condiviso
    # con l'orchestrator per permettere la lettura dello stato dei task
    DATABASE_URL: str = Field(
        default="sqlite:////shared_db/clinical_twin.db"
    )
    # Chiave per la firma dei token JWT — obbligatoria, nessun default
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    # Durata del token: 1440 minuti = 24 ore
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    # Origini autorizzate per le richieste CORS dal browser
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173"]
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()