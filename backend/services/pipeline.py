# File: backend/services/pipeline.py
"""
Worker Asincrono per l'orchestrazione delle pipeline.
Esegue l'estrazione feature (Mock Nextflow) e, in cascata, l'inferenza statistica (R).
Non blocca MAI il thread principale di FastAPI.
"""
import asyncio
import os
import csv
import random
import logging
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.config import settings
from models.domain import Task
from services.inference import InferenceOrchestrator

logger = logging.getLogger(__name__)

async def run_mock_nextflow(task_id: int, model_name: str):
    """
    Task in background che simula Nextflow e avvia l'inferenza R.
    """
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        logger.error(f"Task {task_id} non trovato nel DB. Interruzione pipeline.")
        db.close()
        return
        
    try:
        logger.info(f"🎯 [PIPELINE] Avvio Task {task_id}. Modello: {model_name}")
        
        # 1. Stato: Elaborazione Nextflow
        task.status = "PROCESSING"
        task.progress = 10.0
        db.commit()

        logger.info(f"⚙️ [NEXTFLOW MOCK] Estrazione feature radiomiche...")
        await asyncio.sleep(10)  # Simulazione tempo di calcolo (ridotto per comodità)

        # Selezione feature in base al modello
        if model_name == "HC_vs_svPPA":
            exact_features = [
                "original_firstorder_Minimum.1", "original_firstorder_Energy.4", 
                "original_firstorder_Skewness.4", "original_glcm_DifferenceEntropy.4",
                "original_glcm_DifferenceVariance.4", "original_glrlm_LongRunEmphasis.4",
                "original_glrlm_ShortRunEmphasis.4", "original_firstorder_Energy.14",
                "original_firstorder_Skewness.28", "original_firstorder_Energy.31",
                "original_firstorder_Skewness.31", "original_glszm_SmallAreaEmphasis.31",
                "original_glcm_Idmn.38", "original_gldm_SmallDependenceLowGrayLevelEmphasis.38",
                "original_glcm_Correlation.62", "original_gldm_DependenceNonUniformity.65",
                "original_glcm_Idmn.67", "original_firstorder_10Percentile.71",
                "original_firstorder_Minimum.71", "original_gldm_DependenceEntropy.71",
                "original_firstorder_Energy.72", "original_glszm_GrayLevelNonUniformity.72",
                "original_gldm_DependenceNonUniformity.72", "original_glcm_Imcl.77"
            ]
        elif model_name == "HC_vs_bvFTD":
            exact_features = [
                "original_firstorder_Energy.71", "original_glszm_LargeAreaEmphasis.74",
                "original_glszm_ZoneVariance.4", "original_glszm_ZoneVariance.69",
                "original_glszm_ZoneVariance.74", "original_glszm_LargeAreaHighGrayLevelEmphasis.74",
                "original_firstorder_Energy.76", "original_glcm_Idn.69",
                "original_firstorder_Energy.36"
            ]
        elif model_name == "HC_vs_nfvPPA":
            exact_features = [
                "original_firstorder_Energy", "original_glcm_ClusterShade", "original_glcm_InverseVariance.2",
                "original_gldm_GrayLevelNonUniformity.2", "original_glcm_ClusterShade.16", "original_firstorder_Energy.18",
                "original_firstorder_Minimum.21", "original_gldm_DependenceNonUniformity.22", "original_firstorder_Skewness.31",
                "original_glrlm_GrayLevelNonUniformity.64", "original_gldm_GrayLevelNonUniformity.69"
            ]
        else:
            exact_features = ["feature_sconosciuta"]

        mock_patient_data = [round(random.uniform(0.1, 10.0), 4) for _ in exact_features]

        # Creazione del CSV usando le costanti di configurazione
        output_filename = f"features_{task_id}.csv"
        output_path = os.path.join(settings.FEATURES_DIR, output_filename)
        
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(exact_features)      
            writer.writerow(mock_patient_data)   

        logger.info(f"✅ [NEXTFLOW MOCK] CSV generato: {output_path}")

        # 2. Stato: Avvio Inferenza R
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