# File: model_service/services/inference.py
#
# Orchestratore del ciclo di vita dell'inferenza statistica.
# Responsabilità:
#   1. Interrogare il Model Registry MLflow/DagsHub per individuare
#      il modello con alias 'champion' e scaricarne gli artefatti.
#   2. Recuperare i metadati della run (tag brain_segmenter, run_id…).
#   3. Inviare il trigger asincrono all'inference engine R (Plumber).
#
# Le operazioni MLflow sono sincrone e bloccanti: vengono eseguite
# su thread separati via asyncio.to_thread per non bloccare l'event loop.

import asyncio
import glob
import logging
import os
import shutil

import httpx
import mlflow.artifacts
from mlflow import MlflowClient

from core.config import settings

logger = logging.getLogger(__name__)


class InferenceOrchestrator:

    def __init__(self):
        # MlflowClient legge automaticamente MLFLOW_TRACKING_URI,
        # MLFLOW_TRACKING_USERNAME e MLFLOW_TRACKING_PASSWORD dalle env var.
        self.client = MlflowClient()
        self.r_engine_url = settings.R_ENGINE_URL

    def get_champion_uri(self, model_name: str) -> str:
        """Restituisce l'URI MLflow del modello con alias 'champion'."""
        filter_string = f"name = '{model_name}'"
        models = self.client.search_registered_models(filter_string=filter_string)

        if not models:
            raise ValueError(f"Nessun modello trovato con nome '{model_name}' su DagsHub.")

        model = models[0]

        if "champion" not in model.aliases:
            raise ValueError(f"Nessun alias 'champion' trovato per il modello '{model.name}'.")

        return f"models:/{model.name}@champion"

    def _sync_get_model_info(self, model_name: str) -> dict:
        """
        Recupera i metadati del modello champion da MLflow (operazione sincrona).
        Naviga dal registered model → alias champion → version → run per leggere i tag.
        """
        filter_string = f"name = '{model_name}'"
        models = self.client.search_registered_models(filter_string=filter_string)

        if not models:
            raise ValueError(f"Nessun modello trovato con nome '{model_name}' su DagsHub.")

        model = models[0]

        if "champion" not in model.aliases:
            raise ValueError(f"Nessun alias 'champion' trovato per il modello '{model.name}'.")

        version_number = model.aliases["champion"]
        model_version = self.client.get_model_version(model.name, version_number)
        run = self.client.get_run(model_version.run_id)

        brain_segmenter = run.data.tags.get("brain_segmenter", "freesurfer")
        logger.info(f"Modello '{model_name}' — brain_segmenter: {brain_segmenter}")

        return {
            "model_name": model_name,
            "brain_segmenter": brain_segmenter,
            "run_id": model_version.run_id,
            "tags": run.data.tags,
        }

    async def get_model_info(self, model_name: str) -> dict:
        """Wrapper asincrono di _sync_get_model_info."""
        return await asyncio.to_thread(self._sync_get_model_info, model_name)

    def _sync_download_and_find_rds(self, model_uri: str, model_name: str) -> str:
        """
        Scarica gli artefatti del modello da MLflow nella directory condivisa.
        La cache precedente viene eliminata prima del download per garantire
        che il modello in uso corrisponda sempre alla versione champion corrente.
        Restituisce il path assoluto del primo file .rds trovato.
        """
        download_path = os.path.join(settings.SHARED_VOLUME_DIR, "models", model_name)

        if os.path.exists(download_path):
            logger.info(f"Pulizia cache modello in {download_path}...")
            shutil.rmtree(download_path)

        os.makedirs(download_path, exist_ok=True)

        logger.info("Download artefatti da MLflow in corso...")
        local_model_dir = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=download_path,
        )

        rds_files = glob.glob(f"{local_model_dir}/**/*.rds", recursive=True)
        if not rds_files:
            raise FileNotFoundError(
                "MLflow non ha restituito nessun file .rds. Verificare l'artefatto su DagsHub."
            )

        return rds_files[0]

    async def trigger_r_inference(
        self, task_id: int, model_name: str, skip_mlflow: bool = False
    ) -> dict:
        try:
            if skip_mlflow:
                # Percorso convenzionale usato quando il modello è già presente
                # nella directory condivisa (es. re-run senza aggiornamento del champion).
                exact_rds_path = os.path.join(
                    settings.SHARED_VOLUME_DIR, "models", model_name, "model.rds"
                )
                logger.info(f"Task {task_id}: skip_mlflow=True, uso cache locale.")
            else:
                model_uri = self.get_champion_uri(model_name)
                logger.info(f"Task {task_id}: modello champion -> {model_uri}")
                exact_rds_path = await asyncio.to_thread(
                    self._sync_download_and_find_rds, model_uri, model_name
                )

            logger.info(f"Task {task_id}: file modello R -> {exact_rds_path}")

            async with httpx.AsyncClient() as client:
                payload = {
                    "task_id": str(task_id),
                    "model_name": model_name,
                    "model_dir": exact_rds_path,
                }
                response = await client.post(self.r_engine_url, json=payload, timeout=60.0)

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Inference engine R ha risposto con errore {response.status_code}: {response.text}"
                    )
                return response.json()

        except Exception as e:
            logger.error(f"Errore inferenza task {task_id}: {e}")
            raise