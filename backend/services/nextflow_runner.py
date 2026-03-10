# File: backend/services/nextflow_runner.py
"""
Wrapper Asincrono per l'orchestrazione della pipeline Nextflow.
Esegue il bridge tra il motore di calcolo del team Data Science e il nostro Backend.
"""
import asyncio
import os
import shutil
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class NextflowRunner:
    def __init__(self):
        # Il percorso della pipeline verrà letto dalle variabili d'ambiente (.env).
        # Se non esiste, usiamo un percorso fittizio di default.
        self.pipeline_script = os.getenv("NEXTFLOW_SCRIPT_PATH", "/app/pipeline/main.nf")

    async def extract_features(self, task_id: int, nifti_filename: str, model_name: str = None) -> str:        
        """
        Avvia Nextflow come sottoprocesso asincrono per non bloccare FastAPI.
        """
        # 1. Costruzione dei percorsi
        input_path = os.path.join(settings.NIFTI_DIR, nifti_filename)
        
        # Creiamo un ambiente isolato (sandbox) per l'output di questo specifico task
        # Questo previene la sovrascrittura se analizziamo 2 pazienti contemporaneamente
        temp_outdir = os.path.join(settings.SHARED_VOLUME_DIR, f"temp_nf_{task_id}")
        os.makedirs(temp_outdir, exist_ok=True)

        logger.info(f"🚀 Avvio Nextflow per Task {task_id} sul file {nifti_filename}...")

        # 2. Composizione del comando fornito dal team MLOps
        cmd = [
            "nextflow", 
            "run", 
            self.pipeline_script,
            "--image", input_path,
            "--outdir", temp_outdir
        ]

        # 3. Esecuzione Asincrona (Non bloccante)
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # 4. Gestione Errori
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"🚨 Errore Nextflow (Task {task_id}):\n{error_msg}")
            # Pulizia cartella in caso di errore
            shutil.rmtree(temp_outdir, ignore_errors=True)
            raise RuntimeError(f"Il motore Nextflow è andato in crash: {error_msg}")

        # 5. Adattamento Output (Rename & Move)
        generated_csv = os.path.join(temp_outdir, "radiomics_features.csv")
        
        if not os.path.exists(generated_csv):
            shutil.rmtree(temp_outdir, ignore_errors=True)
            raise FileNotFoundError(f"Nextflow ha terminato, ma non ha generato 'radiomics_features.csv'")

        final_csv_name = f"features_{task_id}.csv"
        final_csv_path = os.path.join(settings.FEATURES_DIR, final_csv_name)
        
        # Spostiamo e rinominiamo il file per il nostro microservizio R e per l'LLM
        shutil.move(generated_csv, final_csv_path)
        
        # 6. Pulizia Sandbox
        shutil.rmtree(temp_outdir, ignore_errors=True)

        logger.info(f"✅ Estrazione completata con successo! CSV salvato in: {final_csv_path}")
        return final_csv_path