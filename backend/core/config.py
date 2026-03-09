# File: backend/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings
import os
from typing import List, Optional

# --- CALCOLO DINAMICO DELLA CARTELLA DATI ---
# Calcola il percorso assoluto: backend/data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Creiamo fisicamente la cartella se non esiste, per prevenire crash al primo avvio
os.makedirs(DATA_DIR, exist_ok=True)

class Settings(BaseSettings):
    # Database
    # Modificato: Usa la cartella data/ dinamicamente
    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'clinical_twin.db')}", 
        description="URL DB Principale"
    )
    
    # MLflow DB (Se viene interrogato in locale)
    MLFLOW_DB_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'mlflow.db')}", 
        description="URL DB MLflow"
    )

    # --- VARIABILI D'AMBIENTE ESTERNE (MLflow / DagsHub) ---
    # Opzione 2: Dichiariamo esplicitamente i campi che FastAPI troverà nel .env
    MLFLOW_TRACKING_USERNAME: Optional[str] = Field(default=None, description="Username per MLflow Tracking")
    MLFLOW_TRACKING_PASSWORD: Optional[str] = Field(default=None, description="Password/Token per MLflow Tracking")
    MLFLOW_TRACKING_URI: Optional[str] = Field(default=None, description="URI remoto per MLflow (es. DagsHub)")
    DAGSHUB_USERNAME: Optional[str] = Field(default=None, description="Username account DagsHub")
    DAGSHUB_TOKEN: Optional[str] = Field(default=None, description="Token di accesso DagsHub")
    REPO_OWNER: Optional[str] = Field(default=None, description="Proprietario della repository DagsHub")
    REPO_NAME: Optional[str] = Field(default=None, description="Nome della repository DagsHub")
    
    # Volumi Condivisi Docker
    SHARED_VOLUME_DIR: str = Field(default="/shared_data", description="Root del volume condiviso")

    # Sicurezza (JWT)
    SECRET_KEY: str = Field(default="clinical-twin-super-secret-key-change-me", description="Chiave segreta per firmare i JWT")
    ALGORITHM: str = Field(default="HS256", description="Algoritmo crittografico JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Scadenza token in minuti (24h)")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174"], 
        description="Origini consentite per le chiamate API dal Frontend"
    )

    @property
    def NIFTI_DIR(self) -> str:
        path = os.path.join(self.SHARED_VOLUME_DIR, "nifti")
        os.makedirs(path, exist_ok=True)
        return path

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

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()