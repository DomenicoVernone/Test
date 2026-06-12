# File: llm_service/main.py
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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


_dev = os.getenv("ENV") == "development"

app = FastAPI(
    title="Clinical Twin — LLM Service",
    description="Assistente AI context-aware per la diagnosi differenziale",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if _dev else None,
    redoc_url="/redoc" if _dev else None,
    openapi_url="/openapi.json" if _dev else None,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["server"] = "webserver"
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["x-xss-protection"] = "1; mode=block"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "llm_service"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "llm_service"}
