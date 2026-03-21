import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SHARED_VOLUME_DIR: str = Field(default="/shared_data")
    GROQ_API_KEY: Optional[str] = Field(default=None)
    SECRET_KEY: str = Field(default="clinical-twin-super-secret-key-change-me")
    ALGORITHM: str = Field(default="HS256")
    CORS_ORIGINS: list = Field(
        default=["http://localhost:5173", "http://localhost:5174"]
    )

    @property
    def RESULTS_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "results")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def FEATURES_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "features")
        os.makedirs(path, exist_ok=True)
        return path

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()