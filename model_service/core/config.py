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