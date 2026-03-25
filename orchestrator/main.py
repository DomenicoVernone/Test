# orchestrator/main.py
#
# Punto di ingresso dell'Orchestrator. Configura l'applicazione FastAPI,
# inizializza il database e monta il router di analisi.
# Questo servizio è esposto solo su loopback (127.0.0.1:8001) —
# il frontend lo raggiunge direttamente per le operazioni sui task.

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from core.config import settings

Base.metadata.create_all(bind=engine)

# Creazione directory del volume condiviso all'avvio
os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "nifti"), exist_ok=True)
os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "features"), exist_ok=True)
os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "results"), exist_ok=True)

from routers import analyze

app = FastAPI(
    title="Clinical Twin — Orchestrator",
    description="Gestione task asincroni e pipeline neuroimaging",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "orchestrator"}