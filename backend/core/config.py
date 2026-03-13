# File: backend/core/config.py
"""
Modulo di Configurazione: Gestore delle Variabili d'Ambiente e Path Architetturali.
Centralizza la configurazione dell'applicazione FastAPI estendendo BaseSettings di Pydantic.

Nota Architetturale: Il modulo risolve dinamicamente i percorsi assoluti al runtime per 
garantire l'indipendenza dalla working directory di esecuzione, creando preventivamente
le directory necessarie per prevenire I/O errors all'avvio del demone FastAPI.
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- RISOLUZIONE DINAMICA DEI PERCORSI ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Creazione preventiva directory dati locale
os.makedirs(DATA_DIR, exist_ok=True)


class Settings(BaseSettings):
    """
    Classe di configurazione tipizzata. 
    Mappa le variabili d'ambiente (.env) agli attributi di classe con validazione runtime.
    """
    
    # --- DATABASE LOCALE ---
    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'clinical_twin.db')}", 
        description="Stringa di connessione SQLAlchemy per il DB transazionale principale"
    )
    
    MLFLOW_DB_URL: str = Field(
        default=f"sqlite:///{os.path.join(DATA_DIR, 'mlflow.db')}", 
        description="Stringa di connessione per il tracking server MLflow locale"
    )

    # --- INTEGRAZIONE ESTERNA (MLflow / DagsHub) ---
    MLFLOW_TRACKING_USERNAME: Optional[str] = Field(default=None, description="Username per MLflow Tracking")
    MLFLOW_TRACKING_PASSWORD: Optional[str] = Field(default=None, description="Password/Token per MLflow Tracking")
    MLFLOW_TRACKING_URI: Optional[str] = Field(default=None, description="URI remoto per MLflow (es. DagsHub)")
    DAGSHUB_USERNAME: Optional[str] = Field(default=None, description="Username account DagsHub")
    DAGSHUB_TOKEN: Optional[str] = Field(default=None, description="Token di accesso API DagsHub")
    REPO_OWNER: Optional[str] = Field(default=None, description="Proprietario della repository DagsHub")
    REPO_NAME: Optional[str] = Field(default=None, description="Nome della repository DagsHub")

    # --- MICROSERVIZI INTERNI ---
    R_ENGINE_URL: str = Field(default="http://inference_engine:8000/infer", description="URL interno del container R per l'inferenza")
    NEXTFLOW_WORKER_URL: str = Field(default="http://nextflow_worker:8002", description="URL interno del container Nextflow Worker")
    
    # --- VOLUMI CONDIVISI (Docker / Host) ---
    SHARED_VOLUME_DIR: str = Field(default="/shared_data", description="Mount point root del volume condiviso tra i container")

    # --- SICUREZZA API (JWT) ---
    SECRET_KEY: str = Field(default="clinical-twin-super-secret-key-change-me", description="Chiave crittografica simmetrica per firma JWT")
    ALGORITHM: str = Field(default="HS256", description="Algoritmo di hashing JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="TTL del token JWT di accesso (24h)")

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174"], 
        description="Whitelist delle origini consentite per il middleware CORS"
    )

    # --- PROPRIETÀ DINAMICHE DEI PATH ---
    # NOTA ARCHITETTURALE: L'uso dei property decorator garantisce la lazy evaluation dei path.
    # Questo assicura che la risoluzione di SHARED_VOLUME_DIR avvenga solo dopo 
    # che Pydantic ha terminato l'override dei valori letti dal file .env.
    
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

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"  # Evita crash se il .env contiene variabili estranee non mappate qui
    )

settings = Settings()