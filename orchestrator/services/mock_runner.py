# orchestrator/services/mock_runner.py
#
# Runner simulato per lo sviluppo e il testing senza Nextflow.
# Genera feature radiomiche fittizie ma strutturalmente coerenti
# con quelle attese dai modelli KNN in produzione.
# Attivabile tramite la variabile USE_MOCK=true nel .env.

import os
import csv
import random
import asyncio
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Feature attese da ciascun modello — devono corrispondere esattamente
# alle colonne prodotte dalla pipeline Nextflow reale
MOCK_FEATURES = {
    "HC_vs_svPPA": [
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
    ],
    "HC_vs_bvFTD": [
        "original_firstorder_Energy.71", "original_glszm_LargeAreaEmphasis.74",
        "original_glszm_ZoneVariance.4", "original_glszm_ZoneVariance.69",
        "original_glszm_ZoneVariance.74", "original_glszm_LargeAreaHighGrayLevelEmphasis.74",
        "original_firstorder_Energy.76", "original_glcm_Idn.69",
        "original_firstorder_Energy.36"
    ],
    "HC_vs_nfvPPA": [
        "original_firstorder_Energy", "original_glcm_ClusterShade",
        "original_glcm_InverseVariance.2", "original_gldm_GrayLevelNonUniformity.2",
        "original_glcm_ClusterShade.16", "original_firstorder_Energy.18",
        "original_firstorder_Minimum.21", "original_gldm_DependenceNonUniformity.22",
        "original_firstorder_Skewness.31", "original_glrlm_GrayLevelNonUniformity.64",
        "original_gldm_GrayLevelNonUniformity.69"
    ],
}

class MockRunner:
    async def extract_features(
        self, task_id: int, nifti_filename: str, model_name: str, **kwargs
    ) -> str:
        logger.info(f"[MOCK] Generazione feature simulate per Task {task_id} ({nifti_filename})")
        await asyncio.sleep(4)

        features = MOCK_FEATURES.get(model_name, ["feature_sconosciuta"])

        values = []
        for feature in features:
            if "Energy" in feature:
                values.append(round(random.uniform(700000000.0, 900000000.0), 4))
            elif "Variance" in feature or "Emphasis" in feature:
                values.append(round(random.uniform(10000.0, 50000.0), 4))
            else:
                values.append(round(random.uniform(0.1, 2.0), 4))

        output_path = os.path.join(settings.FEATURES_DIR, f"features_{task_id}.csv")
        with open(output_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(features)
            writer.writerow(values)

        logger.info(f"[MOCK] CSV salvato in: {output_path}")
        return output_path