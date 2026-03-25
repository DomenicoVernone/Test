# File: model_service/main.py
#
# Entry point del microservizio model_service.
# Espone due endpoint:
#   POST /infer       — scarica il modello champion da MLflow e triggera l'inference engine R
#   GET  /model_info  — recupera i metadati del modello champion (incluso brain_segmenter)
#
# L'InferenceOrchestrator viene istanziato una sola volta al bootstrap del servizio
# e condiviso tra le request tramite app.state, evitando di ricreare il client MLflow
# ad ogni chiamata.

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.config import settings
from services.inference import InferenceOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creazione directory condivise al bootstrap, non a runtime nelle property
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "features"), exist_ok=True)
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "results"), exist_ok=True)
    os.makedirs(os.path.join(settings.SHARED_VOLUME_DIR, "models"), exist_ok=True)

    app.state.orchestrator = InferenceOrchestrator()
    logger.info("model_service avviato.")
    yield
    logger.info("model_service in shutdown.")


app = FastAPI(
    title="Clinical Twin — Model Service",
    description="Download modelli da MLflow e trigger inferenza R",
    version="1.0.0",
    lifespan=lifespan,
)


class InferRequest(BaseModel):
    task_id: int
    model_name: str


@app.post("/infer")
async def run_inference(req: InferRequest):
    """Scarica il modello champion da MLflow e triggera l'inference engine R."""
    try:
        result = await app.state.orchestrator.trigger_r_inference(
            task_id=req.task_id,
            model_name=req.model_name,
        )
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Errore inferenza task {req.task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model_info/{model_name}")
async def get_model_info(model_name: str):
    """
    Recupera i metadati del modello champion da MLflow.
    Restituisce i tag della run, tra cui 'brain_segmenter'.
    Chiamato dall'orchestrator prima di avviare la pipeline Nextflow.
    """
    try:
        info = await app.state.orchestrator.get_model_info(model_name)
        return info
    except Exception as e:
        logger.error(f"Errore recupero info modello '{model_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "model_service"}