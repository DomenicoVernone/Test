# orchestrator/core/database.py
#
# Configurazione del database SQLite condiviso con api_gateway.
# WAL mode abilitato per permettere letture concorrenti durante
# le scritture degli aggiornamenti di stato dei task.

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