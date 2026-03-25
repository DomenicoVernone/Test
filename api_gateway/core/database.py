# api_gateway/core/database.py
#
# Configurazione del database SQLite tramite SQLAlchemy.
# Il WAL mode (Write-Ahead Logging) è abilitato su ogni connessione
# per permettere letture concorrenti mentre un task è in scrittura —
# necessario dato che orchestrator e api_gateway condividono lo stesso DB.

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 15
    }
)

@event.listens_for(engine, "connect")
def set_wal_mode(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()