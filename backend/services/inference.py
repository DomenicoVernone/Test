# File: backend/services/inference.py

import httpx
from mlflow import MlflowClient
import mlflow.artifacts
from fastapi import HTTPException
import logging
import os
import shutil
import glob

logger = logging.getLogger(__name__)

class InferenceOrchestrator:
    def __init__(self):
        self.client = MlflowClient()
        self.r_engine_url = "http://inference_engine:8000/infer"

    def get_champion_uri(self, model_name: str) -> str:
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
            raise HTTPException(status_code=500, detail=f"Errore nel Model Registry: {str(e)}")

    async def trigger_r_inference(self, task_id: str, model_name: str) -> dict:
        try:
            # 1. Recupero URI da MLflow
            model_uri = self.get_champion_uri(model_name)
            logger.info(f"Task {task_id}: Trovato modello champion con URI -> {model_uri}")

            # 2. CACHING E PULIZIA (La Best Practice)
            download_path = f"/shared_data/models/{model_name}"
            
            # Se la cartella esiste, la SVUOTIAMO per evitare conflitti con vecchi modelli "fantasma"
            if os.path.exists(download_path):
                logger.info(f"Pulizia vecchia cache del modello in {download_path}...")
                shutil.rmtree(download_path)
            
            os.makedirs(download_path, exist_ok=True)
            
            # 3. Download "Fresco" del modello Champion
            logger.info("Scaricamento artefatti da MLflow in corso...")
            local_model_dir = mlflow.artifacts.download_artifacts(
                artifact_uri=model_uri, 
                dst_path=download_path
            )
            
            # 4. Trova ESATTAMENTE il file .rds scaricato
            rds_files = glob.glob(f"{local_model_dir}/**/*.rds", recursive=True)
            
            if not rds_files:
                raise Exception("MLflow non ha restituito nessun file .rds! Controlla l'artefatto su DagsHub.")
                
            exact_rds_path = rds_files[0] # Prendiamo il primo (e speriamo unico) modello R
            logger.info(f"File modello R esatto trovato in: {exact_rds_path}")

            # 5. Chiamata asincrona al microservizio R (passando il file ESATTO!)
            async with httpx.AsyncClient() as client:
                payload = {
                    "task_id": task_id,
                    "model_name": model_name,
                    "model_dir": exact_rds_path # ORA PASSIAMO IL FILE SPECIFICO!
                }
                
                response = await client.post(self.r_engine_url, json=payload, timeout=60.0)
                
                if response.status_code != 200:
                    raise Exception(f"Il motore R ha restituito errore: {response.text}")
                    
                return response.json()
                
        except Exception as e:
            logger.error(f"Errore durante l'inferenza: {str(e)}")
            raise Exception(str(e))