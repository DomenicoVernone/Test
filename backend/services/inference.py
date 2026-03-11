# File: backend/services/inference.py
"""
Servizio di Orchestrazione dell'Inference Engine.
Comunica con MLflow (DagsHub) per scaricare i modelli Champion e 
invia i trigger asincroni al microservizio R (Plumber).
"""
import httpx
from mlflow import MlflowClient
import mlflow.artifacts
import logging
import os
import shutil
import glob

from core.config import settings

logger = logging.getLogger(__name__)

class InferenceOrchestrator:
    def __init__(self):
        self.client = MlflowClient()
        self.r_engine_url = settings.R_ENGINE_URL # URL interno del container R per l'inferenza

    def get_champion_uri(self, model_name: str) -> str:
        """Interroga il Model Registry per ottenere l'URI del modello 'champion'."""
        try:
            filter_string = f"name = '{model_name}'"
            models = self.client.search_registered_models(filter_string=filter_string)

            if not models:
                raise ValueError(f"Nessun modello trovato con nome '{model_name}' su DagsHub.")

            model = models[0]
            
            if 'champion' in model.aliases:
                return f"models:/{model.name}@champion"
            else:
                raise ValueError(f"Nessun alias 'champion' trovato per il modello {model.name}.")
                
        except Exception as e:
            logger.error(f"Errore MLflow: {str(e)}")
            raise RuntimeError(f"Errore nel Model Registry: {str(e)}")

    async def trigger_r_inference(self, task_id: int, model_name: str) -> dict:
        """
        Scarica il modello da MLflow e triggera l'API R.
        """
        try:
            # 1. Recupero URI da MLflow
            model_uri = self.get_champion_uri(model_name)
            logger.info(f"Task {task_id}: Trovato modello champion con URI -> {model_uri}")

            # 2. Caching e Pulizia (usando la configurazione centralizzata)
            models_dir = os.path.join(settings.SHARED_VOLUME_DIR, "models")
            download_path = os.path.join(models_dir, model_name)
            
            if os.path.exists(download_path):
                logger.info(f"Pulizia vecchia cache del modello in {download_path}...")
                shutil.rmtree(download_path)
            
            os.makedirs(download_path, exist_ok=True)
            
            # 3. Download da MLflow
            logger.info("Scaricamento artefatti da MLflow in corso...")
            local_model_dir = mlflow.artifacts.download_artifacts(
                artifact_uri=model_uri, 
                dst_path=download_path
            )
            
            # 4. Ricerca del file .rds scaricato
            rds_files = glob.glob(f"{local_model_dir}/**/*.rds", recursive=True)
            if not rds_files:
                raise FileNotFoundError("MLflow non ha restituito nessun file .rds! Controlla l'artefatto su DagsHub.")
                
            exact_rds_path = rds_files[0]
            logger.info(f"File modello R esatto trovato in: {exact_rds_path}")

            # 5. Chiamata asincrona al microservizio R
            async with httpx.AsyncClient() as client:
                payload = {
                    "task_id": str(task_id),
                    "model_name": model_name,
                    "model_dir": exact_rds_path
                }
                
                response = await client.post(self.r_engine_url, json=payload, timeout=60.0)
                
                if response.status_code != 200:
                    raise RuntimeError(f"Il motore R ha restituito errore {response.status_code}: {response.text}")
                    
                return response.json()
                
        except Exception as e:
            logger.error(f"Errore durante l'inferenza del Task {task_id}: {str(e)}")
            raise e