# File: backend/core/database.py
"""
Modulo di configurazione del Database.
Gestisce l'inizializzazione del motore SQLAlchemy e la session factory per SQLite.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Importiamo la configurazione centralizzata
from core.config import settings

# Creazione del motore del database
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
# Creazione della fabbrica di sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base per i modelli (ORM)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency FastAPI per iniettare la sessione del database.
    Garantisce l'apertura e la chiusura sicura della connessione ad ogni richiesta HTTP.
    
    Yields:
        Session: Oggetto sessione di SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()