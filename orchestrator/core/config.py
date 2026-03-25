# orchestrator/core/config.py
#
# Configurazione centralizzata del servizio tramite pydantic-settings.
# Le variabili vengono lette dal file .env — vedere .env.example in root.

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database condiviso con api_gateway sullo stesso volume Docker
    DATABASE_URL: str = Field(default="sqlite:////shared_db/clinical_twin.db")

    # Chiave JWT — deve coincidere con quella di api_gateway per validare i token
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")

    # URL dei servizi interni sulla rete Docker (nome container:porta interna)
    MODEL_SERVICE_URL: str = Field(default="http://model_service:8000")
    NEXTFLOW_WORKER_URL: str = Field(default="http://nextflow_worker:8000")
    AUTH_SERVICE_URL: str = Field(default="http://api_gateway:8000")

    # Path del volume condiviso dentro il container
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")

    # Flag per usare il mock runner invece di Nextflow (sviluppo/test)
    USE_MOCK: bool = Field(default=False)

    # Origini autorizzate per le richieste CORS dal browser
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173"]
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def NIFTI_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "nifti")

    @property
    def FEATURES_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "features")

    @property
    def RESULTS_DIR(self) -> str:
        import os
        return os.path.join(self.SHARED_VOLUME_DIR, "results")

settings = Settings()