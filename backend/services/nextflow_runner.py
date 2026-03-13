import asyncio
import os
import shutil
import logging
import httpx
from core.config import settings

logger = logging.getLogger(__name__)

class NextflowRunner:
    def __init__(self):
        # URL interno del container Nextflow Worker (definito in config.py)
        self.worker_url = settings.NEXTFLOW_WORKER_URL

    async def extract_features(self, task_id: int, nifti_filename: str, model_name: str = None) -> str:        
        # 1. Costruzione dei percorsi nel Volume Condiviso
        input_path = os.path.join(settings.NIFTI_DIR, nifti_filename)
        temp_outdir = os.path.join(settings.SHARED_VOLUME_DIR, f"temp_nf_{task_id}")
        os.makedirs(temp_outdir, exist_ok=True)

        logger.info(f"🚀 Invio richiesta al Nextflow Worker per Task {task_id}...")

        # 2. Composizione del payload da inviare al Worker
        payload = {
            "task_id": str(task_id),
            "input_path": input_path,
            "outdir": temp_outdir
        }

        # Inizializziamo il client HTTP per avviare il job e fare il polling
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.worker_url}/start_preprocessing", json=payload)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"🚨 Impossibile contattare il Nextflow Worker: {e}")
                shutil.rmtree(temp_outdir, ignore_errors=True)
                raise RuntimeError(f"Nextflow Worker offline o errore di rete: {e}")

            generated_csv = os.path.join(temp_outdir, "radiomics_features.csv")
            logger.info(f"⏳ Nextflow in esecuzione. Attesa del file {generated_csv} o di segnali di errore...")
            
            while True:
                if os.path.exists(generated_csv):
                    logger.info(f"✅ CSV trovato sul disco per il task {task_id}!")
                    break

                try:
                    status_response = await client.get(f"{self.worker_url}/status/{task_id}")
                    if status_response.status_code == 200:
                        worker_status = status_response.json().get("status")
                        
                        if worker_status == "FAILED":
                            logger.error(f"❌ Nextflow Worker ha comunicato un FALLIMENTO per il task {task_id}!")
                            shutil.rmtree(temp_outdir, ignore_errors=True) # Puliamo la cartella inutile
                            raise RuntimeError(f"Il processo Nextflow è fallito internamente.")
                except httpx.RequestError as e:
                    logger.warning(f"⚠️ Errore di rete temporaneo durante il check di stato: {e}")

                # Se non c'è il CSV e il task non è FAILED, aspetta 15 secondi
                await asyncio.sleep(15)

        # 5. Adattamento Output
        final_csv_name = f"features_{task_id}.csv"
        final_csv_path = os.path.join(settings.FEATURES_DIR, final_csv_name)
        
        shutil.move(generated_csv, final_csv_path)
        shutil.rmtree(temp_outdir, ignore_errors=True)

        logger.info(f"✅ Estrazione completata! CSV salvato in: {final_csv_path}")
        return final_csv_path