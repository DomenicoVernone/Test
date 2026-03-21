import asyncio
import os
import shutil
import logging
import httpx
import glob 
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

        payload = {
            "task_id": str(task_id),
            "input_path": input_path,
            "outdir": temp_outdir
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.worker_url}/start_preprocessing", json=payload)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"🚨 Impossibile contattare il Nextflow Worker: {e}")
                # shutil.rmtree(temp_outdir, ignore_errors=True)
                raise RuntimeError(f"Nextflow Worker offline: {e}")

            logger.info(f"⏳ Nextflow in esecuzione. Attesa del file CSV o di segnali di errore...")
            
            generated_csv = None

            while True:
                # Cerca il CSV ovunque nella cartella
                csv_files = glob.glob(f"{temp_outdir}/**/*.csv", recursive=True)
                
                if csv_files:
                    generated_csv = csv_files[0]
                    logger.info(f"✅ CSV trovato sul disco per il task {task_id}: {generated_csv}")
                    break

                try:
                    status_response = await client.get(f"{self.worker_url}/status/{task_id}")
                    if status_response.status_code == 200:
                        worker_status = status_response.json().get("status")
                        
                        # Se è fallito in modo esplicito
                        if worker_status == "FAILED":
                            logger.error(f"❌ Nextflow Worker ha comunicato un FALLIMENTO per il task {task_id}!")
                            # shutil.rmtree(temp_outdir, ignore_errors=True)
                            raise RuntimeError(f"Il processo Nextflow è fallito internamente.")
                        
                        # Se ha finito ma il file non c'è (Evita il LOOP INFINITO!)
                        if worker_status in ["COMPLETED", "SUCCESS", "FINISHED"]:
                            csv_files = glob.glob(f"{temp_outdir}/**/*.csv", recursive=True)
                            if csv_files:
                                generated_csv = csv_files[0]
                                break
                            else:
                                # shutil.rmtree(temp_outdir, ignore_errors=True)
                                raise RuntimeError("Nextflow ha finito ma non ha pubblicato il CSV (Errore PublishDir)!")

                except httpx.RequestError as e:
                    logger.warning(f"⚠️ Errore di rete temporaneo durante il check: {e}")

                # Aspetta 15 secondi
                await asyncio.sleep(15)

        # 5. Spostamento Output
        final_csv_name = f"features_{task_id}.csv"
        final_csv_path = os.path.join(settings.FEATURES_DIR, final_csv_name)
        
        shutil.move(generated_csv, final_csv_path)
        # shutil.rmtree(temp_outdir, ignore_errors=True)

        logger.info(f"✅ Estrazione completata! CSV salvato in: {final_csv_path}")
        return final_csv_path