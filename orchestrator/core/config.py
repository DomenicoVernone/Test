# orchestrator/core/config.py
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:////shared_db/clinical_twin.db")
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    MODEL_SERVICE_URL: str = Field(default="http://model_service:8000")
    NEXTFLOW_WORKER_URL: str = Field(default="http://nextflow_worker:8000")
    AUTH_SERVICE_URL: str = Field(default="http://api_gateway:8000")
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")
    USE_MOCK: bool = Field(default=False)
    TEST_MODE: bool = Field(default=False)
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173"])

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strength(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError(
                f"SECRET_KEY deve essere >= 64 caratteri (attuale: {len(v)})"
            )
        return v

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
