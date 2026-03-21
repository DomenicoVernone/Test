from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.inference import InferenceOrchestrator
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Clinical Twin — Model Service",
    description="Download modelli da MLflow e trigger inferenza R",
    version="1.0.0"
)

class InferRequest(BaseModel):
    task_id: int
    model_name: str

@app.post("/infer")
async def run_inference(req: InferRequest):
    """Riceve task_id e model_name, scarica il modello champion e triggera R."""
    try:
        orchestrator = InferenceOrchestrator()
        result = await orchestrator.trigger_r_inference(
            task_id=req.task_id,
            model_name=req.model_name,
        )
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Errore inferenza task {req.task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "model_service"}