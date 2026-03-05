from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String) # Il nome della Risonanza (es. paziente_01.nii)
    status = Column(String, default="PENDING") # Stati: PENDING, PROCESSING, COMPLETED, FAILED
    progress = Column(Float, default=0.0) # Utile per la barra di caricamento sul frontend
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Questo collega il Task al Medico che lo ha avviato (Privacy/Multi-tenancy)
    owner_id = Column(Integer, ForeignKey("users.id"))