# File: llm_service/core/config.py
#
# Configurazione centralizzata tramite pydantic-settings.
# Le variabili d'ambiente vengono lette dal file .env a runtime.
#
# SECRET_KEY è obbligatorio: deve corrispondere alla chiave usata da api_gateway
# per firmare i JWT, poiché questo servizio li verifica in autonomia.
# Le property RESULTS_DIR e FEATURES_DIR restituiscono i path senza effetti
# collaterali — la creazione delle directory è delegata al lifespan in main.py.

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")
    GROQ_API_KEY: Optional[str] = Field(default=None)

    # Deve essere identica alla SECRET_KEY di api_gateway per validare i JWT
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")

    AUTH_SERVICE_URL: str = Field(default="http://api_gateway:8000")

    CORS_ORIGINS: list = Field(default=["http://localhost:5173"])

    @property
    def RESULTS_DIR(self) -> str:
        return os.path.join(self.SHARED_VOLUME_DIR, "results")

    @property
    def FEATURES_DIR(self) -> str:
        return os.path.join(self.SHARED_VOLUME_DIR, "features")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()