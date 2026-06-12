# orchestrator/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from sqlalchemy import text

from core.database import engine, Base
from core.config import settings
from core.limiter import limiter

Base.metadata.create_all(bind=engine)

# Migration: aggiunge colonna 'role' se il DB esiste già senza di essa
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
        conn.commit()
    except Exception:
        pass

os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "nifti"), exist_ok=True)
os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "features"), exist_ok=True)
os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "results"), exist_ok=True)

from routers import analyze

_dev = os.getenv("ENV") == "development"

app = FastAPI(
    title="Clinical Twin — Orchestrator",
    description="Gestione task asincroni e pipeline neuroimaging",
    version="1.0.0",
    docs_url="/docs" if _dev else None,
    redoc_url="/redoc" if _dev else None,
    openapi_url="/openapi.json" if _dev else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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

app.include_router(analyze.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "orchestrator"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "orchestrator"}
