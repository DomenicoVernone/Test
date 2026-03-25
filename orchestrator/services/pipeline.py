# orchestrator/services/pipeline.py
#
# Worker asincrono che coordina le fasi della pipeline diagnostica:
# 0. Recupero del tag brain_segmenter da model_service per allineare
#    il segmentatore al modello champion selezionato
# 1. Estrazione feature radiomiche delegata al nextflow_worker
# 2. Inferenza KNN e UMAP delegata a model_service

import logging
import httpx
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.config import settings
from models.domain import Task
from services.mock_runner import MockRunner
from services.nextflow_runner import NextflowRunner

logger = logging.getLogger(__name__)


async def run_full_pipeline(task_id: int, model_name: str):
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        logger.error(f"[ERROR] Task {task_id} non trovato nel database. Interruzione.")
        db.close()
        return

    try:
        logger.info(f"[INFO] Avvio Task {task_id} — Modello: {model_name}")

        task.status = "PROCESSING"
        task.progress = 10.0
        db.commit()

        # FASE 0: RECUPERO METADATI MODELLO
        # Interroga model_service per leggere il tag brain_segmenter dalla run
        # MLflow del modello champion. Garantisce che preprocessing e training
        # usino lo stesso segmentatore, evitando disallineamenti nelle feature.
        brain_segmenter = "freesurfer"
        try:
            async with httpx.AsyncClient() as client:
                info_response = await client.get(
                    f"{settings.MODEL_SERVICE_URL}/model_info/{model_name}",
                    timeout=30.0
                )
                if info_response.status_code == 200:
                    brain_segmenter = info_response.json().get("brain_segmenter", "freesurfer")
                    logger.info(f"[INFO] Segmentatore recuperato da MLflow: {brain_segmenter}")
                else:
                    logger.warning(
                        f"[WARN] model_service ha risposto {info_response.status_code} "
                        f"per model_info. Uso default: freesurfer"
                    )
        except Exception as e:
            logger.warning(
                f"[WARN] Impossibile recuperare brain_segmenter da model_service: {e}. "
                f"Uso default: freesurfer"
            )

        # FASE 1: ESTRAZIONE FEATURE
        # USE_MOCK=True bypassa Nextflow con dati simulati — utile in sviluppo
        feature_extractor = MockRunner() if settings.USE_MOCK else NextflowRunner()
        await feature_extractor.extract_features(
            task_id=task_id,
            nifti_filename=task.filename,
            model_name=model_name,
            brain_segmenter=brain_segmenter
        )

        # FASE 2: INFERENZA
        task.status = "ANALYZING_R"
        task.progress = 50.0
        db.commit()

        logger.info(f"[INFO] Invio richiesta inferenza a model_service per Task {task_id}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.MODEL_SERVICE_URL}/infer",
                json={"task_id": task_id, "model_name": model_name},
                timeout=120.0
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Model service ha risposto con {response.status_code}: {response.text}"
                )

        task.status = "COMPLETED"
        task.progress = 100.0
        db.commit()
        logger.info(f"[INFO] Task {task_id} completato con successo")

    except Exception as e:
        logger.error(f"[ERROR] Errore critico nel Task {task_id}: {e}")
        task.status = "ERROR"
        db.commit()
    finally:
        db.close()