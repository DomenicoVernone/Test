# File: llm_service/main.py
#
# Entry point del microservizio llm_service.
# Espone il router /chat per la conversazione clinica multi-turno con il modello LLM.
# Il middleware CORS è configurato per accettare richieste dal frontend React.

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "results"), exist_ok=True)
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "features"), exist_ok=True)
    logger.info("llm_service avviato.")
    yield
    logger.info("llm_service in shutdown.")


app = FastAPI(
    title="Clinical Twin — LLM Service",
    description="Assistente AI context-aware per la diagnosi differenziale",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "llm_service"}