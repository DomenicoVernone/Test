import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'clinical_twin.db')}"
    )
    SECRET_KEY: str = Field(default="clinical-twin-super-secret-key-change-me")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174"]
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()