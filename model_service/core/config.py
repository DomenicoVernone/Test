# File: model_service/core/config.py
#
# Configurazione centralizzata tramite pydantic-settings.
# Le variabili d'ambiente vengono lette dal file .env a runtime.
#
# Le credenziali MLflow/DagsHub sono opzionali: se assenti, mlflow
# opera in modalità locale senza tracking remoto.
# Le property FEATURES_DIR e RESULTS_DIR restituiscono i path senza
# creare le directory — la creazione è delegata al lifespan in main.py.

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")
    R_ENGINE_URL: str = Field(default="http://inference_engine:8000/infer")

    MLFLOW_TRACKING_URI: Optional[str] = Field(default=None)
    MLFLOW_TRACKING_USERNAME: Optional[str] = Field(default=None)
    MLFLOW_TRACKING_PASSWORD: Optional[str] = Field(default=None)
    DAGSHUB_USERNAME: Optional[str] = Field(default=None)
    DAGSHUB_TOKEN: Optional[str] = Field(default=None)
    REPO_OWNER: Optional[str] = Field(default=None)
    REPO_NAME: Optional[str] = Field(default=None)

    @property
    def FEATURES_DIR(self) -> str:
        return os.path.join(self.SHARED_VOLUME_DIR, "features")

    @property
    def RESULTS_DIR(self) -> str:
        return os.path.join(self.SHARED_VOLUME_DIR, "results")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()