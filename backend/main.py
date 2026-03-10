# File: backend/main.py
"""
API Gateway Principale (FastAPI).
Punto d'ingresso dell'applicazione. Configura i middleware (CORS), 
inizializza il DB e registra i router dei microservizi.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat

from core.database import engine, Base
from core.config import settings
from routers import auth, analyze

# 1. Inizializzazione del Database
# Crea le tabelle nel database (se non esistono già)
Base.metadata.create_all(bind=engine)

# 2. Inizializzazione dell'applicazione FastAPI
app = FastAPI(
    title="Clinical Twin API",
    description="Gateway asincrono MLOps per l'analisi clinica di risonanze magnetiche",
    version="2.0.0"  
)

# 3. Configurazione CORS (Centralizzata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Registrazione dei Router
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(chat.router)

# 5. Endpoint di Health Check

@app.get("/", tags=["Health"])
def read_root():
    """Endpoint di Health Check per Kubernetes / Docker Compose."""
    return {"status": "ok", "message": "Clinical Twin API Gateway è operativo."}