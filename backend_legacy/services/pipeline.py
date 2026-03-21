"""
Worker Asincrono per l'orchestrazione delle pipeline.
Usa il pattern Strategy per alternare l'estrazione fittizia (Mock) a quella reale (Nextflow).
"""
import logging
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.domain import Task
from services.inference import InferenceOrchestrator

from services.mock_runner import MockRunner
from services.nextflow_runner import NextflowRunner

logger = logging.getLogger(__name__)

# INTERRUTTORE ARCHITETTURALE
USE_MOCK = False 

async def run_full_pipeline(task_id: int, model_name: str):
    """
    Task in background che orchestra l'estrazione dati e l'inferenza R.
    """
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        logger.error(f"Task {task_id} non trovato. Interruzione.")
        db.close()
        return
        
    try:
        logger.info(f"🎯 [PIPELINE] Avvio Task {task_id}. Modello: {model_name}")
        
        # 1. Stato: Elaborazione (Estrazione Feature)
        task.status = "PROCESSING"
        task.progress = 10.0
        db.commit()

        # ==========================================
        # FASE 1: ESTRAZIONE FEATURE (Pattern Strategy)
        # ==========================================
        # Seleziona dinamicamente quale "motore" usare
        feature_extractor = MockRunner() if USE_MOCK else NextflowRunner()
        
        # Chiamata polimorfica (entrambi hanno lo stesso metodo)
        await feature_extractor.extract_features(
            task_id=task_id, 
            nifti_filename=task.filename, 
            model_name=model_name
        )


        # ==========================================
        # FASE 2: INFERENZA STATISTICA E UMAP (R)
        # ==========================================
        task.status = "ANALYZING_R"
        task.progress = 50.0
        db.commit()

        logger.info(f"🧠 [INFERENCE ENGINE] Richiesta esecuzione R...")
        orchestrator = InferenceOrchestrator()
        await orchestrator.trigger_r_inference(task_id=task_id, model_name=model_name)

        # 3. Stato: Completato con successo
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