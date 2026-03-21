# File: backend/services/mock_runner.py
"""
Servizio di simulazione (Mock) per l'estrazione delle feature radiomiche.
Sostituisce temporaneamente la vera pipeline Nextflow durante lo sviluppo.
"""
import os
import csv
import random
import asyncio
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class MockRunner:
    async def extract_features(self, task_id: int, nifti_filename: str, model_name: str) -> str:
        """
        Emula l'interfaccia del NextflowRunner generato dati radiomici fittizi ma realistici.
        """
        logger.info(f"⚙️ [MOCK] Generazione feature radiomiche simulate per l'immagine {nifti_filename}...")
        
        # Simuliamo il tempo di elaborazione di una pipeline
        await asyncio.sleep(4)  

        # Seleziona le feature giuste in base al modello
        if model_name == "HC_vs_svPPA":
            exact_features = ["original_firstorder_Minimum.1", "original_firstorder_Energy.4", "original_firstorder_Skewness.4", "original_glcm_DifferenceEntropy.4", "original_glcm_DifferenceVariance.4", "original_glrlm_LongRunEmphasis.4", "original_glrlm_ShortRunEmphasis.4", "original_firstorder_Energy.14", "original_firstorder_Skewness.28", "original_firstorder_Energy.31", "original_firstorder_Skewness.31", "original_glszm_SmallAreaEmphasis.31", "original_glcm_Idmn.38", "original_gldm_SmallDependenceLowGrayLevelEmphasis.38", "original_glcm_Correlation.62", "original_gldm_DependenceNonUniformity.65", "original_glcm_Idmn.67", "original_firstorder_10Percentile.71", "original_firstorder_Minimum.71", "original_gldm_DependenceEntropy.71", "original_firstorder_Energy.72", "original_glszm_GrayLevelNonUniformity.72", "original_gldm_DependenceNonUniformity.72", "original_glcm_Imcl.77"]
        elif model_name == "HC_vs_bvFTD":
            exact_features = ["original_firstorder_Energy.71", "original_glszm_LargeAreaEmphasis.74", "original_glszm_ZoneVariance.4", "original_glszm_ZoneVariance.69", "original_glszm_ZoneVariance.74", "original_glszm_LargeAreaHighGrayLevelEmphasis.74", "original_firstorder_Energy.76", "original_glcm_Idn.69", "original_firstorder_Energy.36"]
        elif model_name == "HC_vs_nfvPPA":
            exact_features = ["original_firstorder_Energy", "original_glcm_ClusterShade", "original_glcm_InverseVariance.2", "original_gldm_GrayLevelNonUniformity.2", "original_glcm_ClusterShade.16", "original_firstorder_Energy.18", "original_firstorder_Minimum.21", "original_gldm_DependenceNonUniformity.22", "original_firstorder_Skewness.31", "original_glrlm_GrayLevelNonUniformity.64", "original_gldm_GrayLevelNonUniformity.69"]
        else:
            exact_features = ["feature_sconosciuta"]

        # Dati realistici di un paziente
        mock_patient_data = []
        for feature in exact_features:
            if "Energy" in feature:
                mock_patient_data.append(round(random.uniform(700000000.0, 900000000.0), 4))
            elif "Variance" in feature or "Emphasis" in feature:
                mock_patient_data.append(round(random.uniform(10000.0, 50000.0), 4))
            else:
                mock_patient_data.append(round(random.uniform(0.1, 2.0), 4))

        # Scrittura del CSV
        output_filename = f"features_{task_id}.csv"
        output_path = os.path.join(settings.FEATURES_DIR, output_filename)
        
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(exact_features)      
            writer.writerow(mock_patient_data)   
            
        logger.info(f"✅ [MOCK] CSV salvato in: {output_path}")
        return output_path