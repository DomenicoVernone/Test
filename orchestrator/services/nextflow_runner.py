# orchestrator/services/nextflow_runner.py
#
# Client HTTP per il nextflow_worker. Avvia la pipeline di neuroimaging
# tramite richiesta POST e attende il completamento del CSV radiomico
# con polling periodico sullo stato del task.

import asyncio
import os
import shutil
import logging
import httpx
import glob
from core.config import settings

logger = logging.getLogger(__name__)

# Timeout massimo di attesa per il completamento della pipeline.
# FreeSurfer può richiedere fino a 8-10 ore su CPU — il valore è
# conservativo per non interrompere task legittimamente lunghi.
MAX_WAIT_SECONDS = 36000  # 10 ore

class NextflowRunner:
    def __init__(self):
        self.worker_url = settings.NEXTFLOW_WORKER_URL

    async def extract_features(
        self,
        task_id: int,
        nifti_filename: str,
        model_name: str = None,
        brain_segmenter: str = "freesurfer"
    ) -> str:

        input_path = os.path.join(settings.NIFTI_DIR, nifti_filename)
        temp_outdir = os.path.join(settings.SHARED_VOLUME_DIR, f"temp_nf_{task_id}")
        os.makedirs(temp_outdir, exist_ok=True)

        logger.info(f"[INFO] Invio richiesta al Nextflow Worker per Task {task_id} (segmentatore: {brain_segmenter})")

        payload = {
            "task_id": str(task_id),
            "input_path": input_path,
            "outdir": temp_outdir,
            "brain_segmenter": brain_segmenter
        }

        elapsed = 0

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.worker_url}/start_preprocessing",
                    json=payload
                )
                response.raise_for_status()
            except Exception as e:
                logger.error(f"[ERROR] Impossibile contattare il Nextflow Worker: {e}")
                raise RuntimeError(f"Nextflow Worker offline: {e}")

            logger.info(f"[INFO] Nextflow avviato per Task {task_id}. Attesa completamento...")

            generated_csv = None

            while elapsed < MAX_WAIT_SECONDS:
                csv_files = glob.glob(
                    f"{temp_outdir}/**/radiomics_features.csv", recursive=True
                )

                if csv_files:
                    generated_csv = csv_files[0]
                    logger.info(f"[INFO] CSV trovato per Task {task_id}: {generated_csv}")
                    break

                try:
                    status_response = await client.get(
                        f"{self.worker_url}/status/{task_id}"
                    )
                    if status_response.status_code == 200:
                        worker_status = status_response.json().get("status")

                        if worker_status == "FAILED":
                            logger.error(f"[ERROR] Nextflow Worker ha segnalato un fallimento per Task {task_id}")
                            raise RuntimeError("Il processo Nextflow è fallito internamente.")

                        if worker_status in ["COMPLETED", "SUCCESS", "FINISHED"]:
                            csv_files = glob.glob(
                                f"{temp_outdir}/**/radiomics_features.csv", recursive=True
                            )
                            if csv_files:
                                generated_csv = csv_files[0]
                                break
                            else:
                                raise RuntimeError(
                                    "Nextflow ha completato ma il CSV non è stato pubblicato."
                                )

                except httpx.RequestError as e:
                    logger.warning(f"[WARN] Errore di rete temporaneo durante il polling: {e}")

                await asyncio.sleep(15)
                elapsed += 15

            if generated_csv is None:
                raise RuntimeError(
                    f"Timeout: Task {task_id} non completato entro {MAX_WAIT_SECONDS // 3600} ore."
                )

        final_csv_name = f"features_{task_id}.csv"
        final_csv_path = os.path.join(settings.FEATURES_DIR, final_csv_name)
        shutil.move(generated_csv, final_csv_path)

        logger.info(f"[INFO] Estrazione completata. CSV salvato in: {final_csv_path}")
        return final_csv_path