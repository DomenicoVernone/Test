"""
Modulo dei Modelli di Dominio (ORM SQLAlchemy).
Definisce la struttura delle tabelle del database relazionale.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    """
    Modello per gli Utenti (Medici) della piattaforma Clinical Twin.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relazione ORM: un utente può avere più task associati
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    """
    Modello per i Task di elaborazione Risonanze Magnetiche (NIfTI).
    Traccia lo stato di esecuzione asincrona della pipeline Nextflow.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # Il nome del file (es. paziente_01.nii)
    status = Column(String, default="PENDING", nullable=False)  # Stati: PENDING, PROCESSING, COMPLETED, FAILED
    progress = Column(Float, default=0.0)  # Progresso per il frontend (0.0 - 100.0)
    model_name = Column(String, nullable=True)  # Es: HC_vs_bvFTD
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Chiave esterna per il multi-tenancy (Privacy SaMD)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relazione ORM verso l'utente proprietario
    owner = relationship("User", back_populates="tasks")