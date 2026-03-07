# File: backend/services/pipeline.py

import asyncio
import os
import csv
import random
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.domain import Task

async def run_mock_nextflow(task_id: str, filename: str, volume_dir: str, model_name: str):
    db: Session = SessionLocal()
    try:
        print(f"🎯 [NEXTFLOW MOCK] Avvio Task {task_id}. Modello: >>> {model_name} <<<")
        
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
            
        task.status = "PROCESSING"
        db.commit()

        print(f"⚙️ [NEXTFLOW MOCK] Estrazione feature radiomiche per {model_name}...")
        await asyncio.sleep(20) # Simulazione tempo di calcolo

        # --- ROUTING DINAMICO DELLE FEATURE IN BASE AL MODELLO ---
        if model_name == "HC_vs_svPPA":
            # Le 24 feature per il modello KNN (caret)
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
            # Le 9 feature per il modello Random Forest (mlr)
            exact_features = [
                "original_firstorder_Energy.71", "original_glszm_LargeAreaEmphasis.74",
                "original_glszm_ZoneVariance.4", "original_glszm_ZoneVariance.69",
                "original_glszm_ZoneVariance.74", "original_glszm_LargeAreaHighGrayLevelEmphasis.74",
                "original_firstorder_Energy.76", "original_glcm_Idn.69",
                "original_firstorder_Energy.36"
            ]
            
        elif model_name == "HC_vs_nfvPPA":
            # Le 11 feature per il modello XGBoost
            exact_features = [
                "original_firstorder_Energy", "original_glcm_ClusterShade", "original_glcm_InverseVariance.2",
                "original_gldm_GrayLevelNonUniformity.2", "original_glcm_ClusterShade.16", "original_firstorder_Energy.18",
                "original_firstorder_Minimum.21", "original_gldm_DependenceNonUniformity.22", "original_firstorder_Skewness.31",
                "original_glrlm_GrayLevelNonUniformity.64", "original_gldm_GrayLevelNonUniformity.69"
            ]
            
        else:
            # Fallback di sicurezza in caso di modelli non censiti
            exact_features = ["feature_sconosciuta"]

        # -----------------------------------------------------------

        # Generiamo la finta riga del paziente (mock data)
        mock_patient_data = [round(random.uniform(0.1, 10.0), 4) for _ in exact_features]

        # Creiamo il CSV
        output_filename = f"features_{task_id}.csv"
        output_path = os.path.join(volume_dir, output_filename)
        
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(exact_features)      
            writer.writerow(mock_patient_data)   

        print(f"✅ [NEXTFLOW MOCK] CSV perfetto generato: {output_filename}")

        task.status = "NEXTFLOW_COMPLETED"
        task.progress = 100.0
        db.commit()

    except Exception as e:
        task.status = "ERROR"
        db.commit()
        print(f"🚨 [NEXTFLOW MOCK] Errore critico: {e}")
    finally:
        db.close()