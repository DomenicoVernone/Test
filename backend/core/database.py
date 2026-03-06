"""
Moduli di base. Gestisce la connessione a SQLite e fornisce la classe Base per i modelli SQLAlchemy.
"""
from fastapi import FastAPI
# ... resto del codice ...
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurazione del DB SQLite (il file verrà creato automaticamente)
SQLALCHEMY_DATABASE_URL = "sqlite:///./clinical_twin.db"

# Creazione del motore del database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creazione della fabbrica di sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base per i modelli SQLAlchemy
Base = declarative_base()

# Dependency (Yield) per ottenere la sessione del DB nei router
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()