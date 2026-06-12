# File: model_service/main.py
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from services.inference import InferenceOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}


def _validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Modello non valido. Valori accettati: {sorted(ALLOWED_MODELS)}"
        )
    return model_name


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "features"), exist_ok=True)
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "results"), exist_ok=True)
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "models"), exist_ok=True)

    app.state.orchestrator = InferenceOrchestrator()
    logger.info("model_service avviato.")
    yield
    logger.info("model_service in shutdown.")


_dev = os.getenv("ENV") == "development"

app = FastAPI(
    title="Clinical Twin — Model Service",
    description="Download modelli da MLflow e trigger inferenza R",
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


class InferRequest(BaseModel):
    task_id: int
    model_name: str


@app.post("/infer")
async def run_inference(req: InferRequest):
    _validate_model_name(req.model_name)
    try:
        result = await app.state.orchestrator.trigger_r_inference(
            task_id=req.task_id,
            model_name=req.model_name,
        )
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Errore inferenza task {req.task_id}: {e}")
        raise HTTPException(status_code=500, detail="Errore durante l'inferenza. Riprova.")


@app.get("/model_info/{model_name}")
async def get_model_info(model_name: str):
    _validate_model_name(model_name)
    try:
        info = await app.state.orchestrator.get_model_info(model_name)
        return info
    except Exception as e:
        logger.error(f"Errore recupero info modello '{model_name}': {e}")
        raise HTTPException(status_code=404, detail=f"Modello '{model_name}' non trovato o non disponibile.")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "model_service"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "model_service"}
