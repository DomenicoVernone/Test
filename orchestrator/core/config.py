import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database condiviso (stesso volume di api_gateway)
    DATABASE_URL: str = Field(default="sqlite:////shared_db/clinical_twin.db")

    # JWT (stessa chiave di api_gateway per validare i token)
    SECRET_KEY: str = Field(default="clinical-twin-super-secret-key-change-me")
    ALGORITHM: str = Field(default="HS256")

    # Servizi interni
    MODEL_SERVICE_URL: str = Field(default="http://model_service:8003")
    NEXTFLOW_WORKER_URL: str = Field(default="http://nextflow_worker:8002")

    # Volume condiviso
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174"]
    )

    @property
    def NIFTI_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "nifti")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def FEATURES_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "features")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def RESULTS_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "results")
        os.makedirs(path, exist_ok=True)
        return path

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()