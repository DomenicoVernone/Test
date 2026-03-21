"""
Worker Asincrono per l'orchestrazione delle pipeline.
"""
import logging
import httpx
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.config import settings
from models.domain import Task
from services.mock_runner import MockRunner
from services.nextflow_runner import NextflowRunner

logger = logging.getLogger(__name__)

USE_MOCK = False

async def run_full_pipeline(task_id: int, model_name: str):
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        logger.error(f"Task {task_id} non trovato. Interruzione.")
        db.close()
        return

    try:
        logger.info(f"🎯 [PIPELINE] Avvio Task {task_id}. Modello: {model_name}")

        task.status = "PROCESSING"
        task.progress = 10.0
        db.commit()

        # FASE 1: ESTRAZIONE FEATURE
        feature_extractor = MockRunner() if USE_MOCK else NextflowRunner()
        await feature_extractor.extract_features(
            task_id=task_id,
            nifti_filename=task.filename,
            model_name=model_name
        )

        # FASE 2: INFERENZA — chiamata HTTP a model_service
        task.status = "ANALYZING_R"
        task.progress = 50.0
        db.commit()

        logger.info(f"🧠 [MODEL SERVICE] Invio richiesta inferenza...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.MODEL_SERVICE_URL}/infer",
                json={"task_id": task_id, "model_name": model_name},
                timeout=120.0
            )
            if response.status_code != 200:
                raise RuntimeError(f"Model service ha risposto con {response.status_code}: {response.text}")

        task.status = "COMPLETED"
        task.progress = 100.0
        db.commit()
        logger.info(f"🎉 [PIPELINE] Task {task_id} terminato con successo!")

    except Exception as e:
        logger.error(f"🚨 [PIPELINE] Errore critico nel task {task_id}: {e}")
        task.status = "ERROR"
        db.commit()
    finally:
        db.close()
