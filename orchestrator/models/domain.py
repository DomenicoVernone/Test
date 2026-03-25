# orchestrator/models/domain.py
#
# Modelli ORM SQLAlchemy per il database condiviso.
# Definisce User e Task — le due entità centrali del sistema.
# Lo schema è condiviso con api_gateway sullo stesso volume SQLite.

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Un utente può avere più task — cascade garantisce la pulizia
    # automatica dei task se l'utente viene eliminato
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    """Traccia lo stato di esecuzione asincrona della pipeline per ogni risonanza."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    # Stati possibili: PENDING → PROCESSING → ANALYZING_R → COMPLETED / ERROR
    status = Column(String, default="PENDING", nullable=False)
    progress = Column(Float, default=0.0)
    model_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Chiave esterna per isolare i task per utente (multi-tenancy)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks")