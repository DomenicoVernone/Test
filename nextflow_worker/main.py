from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
import shutil
import hashlib
from typing import Optional

# Copia file statici in /tmp all'avvio
shutil.copy2("/app/data/external/ROI_labels.tsv", "/tmp/ROI_labels.tsv")
shutil.copy2("/app/nextflow/configs/pyradiomics.yaml", "/tmp/pyradiomics.yaml")

app = FastAPI()

TASKS_STATUS = {}

CONTAINER_BASE = os.getenv("SHARED_VOLUME_DIR", "/shared_data")
HOST_BASE = os.getenv("HOST_SHARED_VOLUME_DIR", "/shared_data")


class NextflowTask(BaseModel):
    task_id: str
    input_path: str
    outdir: str
    brain_segmenter: Optional[str] = "freesurfer"


def get_nifti_hash(nifti_path: str) -> str:
    """
    Calcola un hash deterministico del nome del file NIfTI.
    Due task che processano la stessa risonanza ottengono la stessa workDir,
    permettendo a Nextflow di riutilizzare la cache di FreeSurfer via -resume.
    Risonanze diverse producono hash diversi e quindi workDir isolate,
    garantendo la sicurezza in caso di esecuzioni parallele.
    """
    return hashlib.md5(os.path.basename(nifti_path).encode()).hexdigest()[:12]


def run_nextflow_pipeline(task_id: str, input_path: str, outdir: str, brain_segmenter: str):

    host_outdir = outdir.replace(CONTAINER_BASE, HOST_BASE)
    os.makedirs(host_outdir, exist_ok=True)

    # La workDir include l'hash del segmentatore oltre a quello del NIfTI:
    # se lo stesso file viene rielaborato con un segmentatore diverso, la cache
    # non viene riutilizzata — comportamento corretto perché l'output cambia.
    nifti_hash = get_nifti_hash(input_path)
    work_dir = f"/tmp/nextflow_work/cache_{nifti_hash}_{brain_segmenter}"
    os.makedirs(work_dir, exist_ok=True)

    tmp_nifti = f"{work_dir}/nifti_{os.path.basename(input_path)}"
    if not os.path.exists(tmp_nifti):
        shutil.copy2(input_path, tmp_nifti)

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
        "-w", work_dir
    ]

    print(f"🔄 Avvio Nextflow per Task {task_id}...")
    print(f"   Input:            {tmp_nifti}")
    print(f"   Outdir:           {host_outdir}")
    print(f"   WorkDir:          {work_dir}")
    print(f"   Brain segmenter:  {brain_segmenter}")

    try:
        subprocess.run(cmd, cwd=work_dir, check=True)
        print(f"✅ Task {task_id} completato!")
        TASKS_STATUS[task_id] = "SUCCESS"
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRORE: Nextflow fallito per il Task {task_id} con codice {e.returncode}")
        TASKS_STATUS[task_id] = "FAILED"


@app.post("/start_preprocessing")
async def start_preprocessing(task: NextflowTask, background_tasks: BackgroundTasks):
    TASKS_STATUS[task.task_id] = "RUNNING"
    background_tasks.add_task(
        run_nextflow_pipeline,
        task.task_id,
        task.input_path,
        task.outdir,
        task.brain_segmenter
    )
    return {"status": "accepted", "message": f"Nextflow avviato per il task {task.task_id}"}


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    status = TASKS_STATUS.get(task_id, "UNKNOWN")
    return {"task_id": task_id, "status": status}