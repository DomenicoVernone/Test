# File: nextflow_worker/main.py
#
# Entry point del microservizio nextflow_worker.
# Espone due endpoint:
#   POST /start_preprocessing — avvia la pipeline Nextflow in background
#   GET  /status/{task_id}    — restituisce lo stato corrente del task
#
# Pattern DooD (Docker-out-of-Docker): il container monta il socket Docker
# dell'host per poter avviare i container Nextflow direttamente sull'host.
# Questo implica che i path dei volumi nei comandi Nextflow devono essere
# path dell'host, non del container — da cui HOST_SHARED_VOLUME_DIR.
#
# NOTA: TASKS_STATUS e' un dizionario in memoria. Gli stati vengono persi
# al riavvio del container. Sufficiente per il contesto corrente.

import asyncio
import hashlib
import logging
import os
import shutil
import subprocess
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TASKS_STATUS = {}

CONTAINER_BASE = os.getenv("SHARED_VOLUME_DIR", "/shared_data")
HOST_BASE = os.getenv("HOST_SHARED_VOLUME_DIR", "/shared_data")

# Lock globale per serializzare l'accesso alla GPU MIG.
# FastSurfer richiede l'intera MIG instance: due esecuzioni concorrenti
# causano un conflitto sul CUDACachingAllocator di PyTorch.
# I task FreeSurfer non sono soggetti a questo vincolo e girano liberamente.
gpu_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Copia dei file statici al bootstrap del servizio.
    # ROI_labels.tsv viene copiato sia in /tmp (fallback per NF_LABELS in nextflow.config)
    # che nel volume condiviso (per inference_engine, che lo legge tramite NF_LABELS).
    # pyradiomics.yaml viene copiato in /tmp come fallback per NF_SETTINGS.
    try:
        shutil.copy2("/app/data/external/ROI_labels.tsv", "/tmp/ROI_labels.tsv")
        shutil.copy2("/app/data/external/ROI_labels.tsv", "/shared_data/ROI_labels.tsv")
        shutil.copy2("/app/nextflow/configs/pyradiomics.yaml", "/tmp/pyradiomics.yaml")
        logger.info("File statici copiati in /tmp e nel volume condiviso.")
    except OSError as e:
        logger.error(f"File statico mancante al bootstrap: {e}. Verificare la directory data/.")
    yield
    logger.info("nextflow_worker in shutdown.")


app = FastAPI(
    title="Clinical Twin — Nextflow Worker",
    description="Pipeline neuroimaging DooD per la segmentazione cerebrale e l'estrazione di feature radiomiche",
    version="1.0.0",
    lifespan=lifespan,
)


class NextflowTask(BaseModel):
    task_id: str
    input_path: str
    outdir: str
    brain_segmenter: Optional[str] = "freesurfer"


def get_nifti_hash(nifti_path: str) -> str:
    """
    Calcola un hash deterministico dal nome del file NIfTI.
    Usato come componente della workDir per isolare le esecuzioni.
    """
    return hashlib.md5(os.path.basename(nifti_path).encode()).hexdigest()[:12]


def run_nextflow_pipeline(task_id: str, input_path: str, outdir: str, brain_segmenter: str):
    host_outdir = outdir.replace(CONTAINER_BASE, HOST_BASE)
    os.makedirs(host_outdir, exist_ok=True)

    # La workDir include hash NIfTI, segmentatore e task_id.
    # Questo garantisce che ogni task abbia una directory isolata,
    # evitando conflitti sul lock di sessione Nextflow in caso di
    # esecuzioni parallele sullo stesso file con lo stesso segmentatore.
    nifti_hash = get_nifti_hash(input_path)
    work_dir = f"/tmp/nextflow_work/cache_{nifti_hash}_{brain_segmenter}_{task_id}"
    os.makedirs(work_dir, exist_ok=True)

    tmp_nifti = f"{work_dir}/nifti_{os.path.basename(input_path)}"
    if not os.path.exists(tmp_nifti):
        shutil.copy2(input_path, tmp_nifti)

    # La licenza FreeSurfer viene copiata in /tmp/freesurfer_license.txt
    # perche' nextflow.config la monta li' nel container via runOptions.
    shutil.copy2("/app/license.txt", "/tmp/freesurfer_license.txt")

    cmd = [
        "nextflow", "run", "/app/nextflow/preprocessing.nf",
        "-c", "/app/nextflow/nextflow.config",
        "-resume",
        "--image", tmp_nifti,
        "--outdir", outdir,
        "--brain_segmenter", brain_segmenter,
        "--fastsurfer_device", "cuda" if brain_segmenter == "fastsurfer" else "cpu",
        "--fastsurfer_threads", "8",
        "-w", work_dir,
    ]

    logger.info(f"Task {task_id}: avvio Nextflow — segmentatore={brain_segmenter}, input={tmp_nifti}")

    try:
        subprocess.run(cmd, cwd=work_dir, check=True)
        logger.info(f"Task {task_id}: completato.")
        TASKS_STATUS[task_id] = "SUCCESS"
    except subprocess.CalledProcessError as e:
        logger.error(f"Task {task_id}: Nextflow fallito con codice {e.returncode}.")
        TASKS_STATUS[task_id] = "FAILED"


async def run_pipeline_with_gpu_lock(task_id: str, input_path: str, outdir: str, brain_segmenter: str):
    """
    Wrapper asincrono per la pipeline Nextflow.
    I task FastSurfer acquisiscono il GPU lock prima di partire: la MIG instance
    non supporta esecuzioni concorrenti di PyTorch. I task FreeSurfer girano
    liberamente senza lock, mantenendo la parallelizzazione CPU.
    """
    if brain_segmenter == "fastsurfer":
        logger.info(f"Task {task_id}: in attesa del GPU lock (FastSurfer)...")
        async with gpu_lock:
            logger.info(f"Task {task_id}: GPU lock acquisito.")
            await asyncio.to_thread(
                run_nextflow_pipeline, task_id, input_path, outdir, brain_segmenter
            )
            logger.info(f"Task {task_id}: GPU lock rilasciato.")
    else:
        await asyncio.to_thread(
            run_nextflow_pipeline, task_id, input_path, outdir, brain_segmenter
        )


@app.post("/start_preprocessing")
async def start_preprocessing(task: NextflowTask, background_tasks: BackgroundTasks):
    TASKS_STATUS[task.task_id] = "RUNNING"
    background_tasks.add_task(
        run_pipeline_with_gpu_lock,
        task.task_id,
        task.input_path,
        task.outdir,
        task.brain_segmenter,
    )
    return {"status": "accepted", "message": f"Nextflow avviato per il task {task.task_id}"}


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    status = TASKS_STATUS.get(task_id, "UNKNOWN")
    return {"task_id": task_id, "status": status}