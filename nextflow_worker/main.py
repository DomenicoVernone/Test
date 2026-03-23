from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
import shutil

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

def run_nextflow_pipeline(task_id: str, input_path: str, outdir: str):

    host_outdir = outdir.replace(CONTAINER_BASE, HOST_BASE)
    os.makedirs(host_outdir, exist_ok=True)

    # Copia il NIfTI in /tmp dove è accessibile dai container DooD
    tmp_nifti = f"/tmp/nextflow_work/nifti_{os.path.basename(input_path)}"
    if not os.path.exists(tmp_nifti):
    	shutil.copy2(input_path, tmp_nifti)
    shutil.copy2("/app/license.txt", "/tmp/freesurfer_license.txt")

    cmd = [
        "nextflow", "run", "/app/nextflow/preprocessing.nf",
        "-c", "/app/nextflow/nextflow.config",
        "-resume",
        "--image", tmp_nifti,
        "--outdir", outdir
    ]

    print(f"🔄 Avvio Nextflow per Task {task_id}...")
    print(f"   Input: {tmp_nifti}")
    print(f"   Outdir: {host_outdir}")

    try:
        subprocess.run(cmd, cwd="/app", check=True)
        print(f"✅ Task {task_id} completato!")
        TASKS_STATUS[task_id] = "SUCCESS"
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRORE: Nextflow fallito per il Task {task_id} con codice {e.returncode}")
        TASKS_STATUS[task_id] = "FAILED"
      
@app.post("/start_preprocessing")
async def start_preprocessing(task: NextflowTask, background_tasks: BackgroundTasks):
    TASKS_STATUS[task.task_id] = "RUNNING"
    background_tasks.add_task(run_nextflow_pipeline, task.task_id, task.input_path, task.outdir)
    return {"status": "accepted", "message": f"Nextflow avviato per il task {task.task_id}"}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    status = TASKS_STATUS.get(task_id, "UNKNOWN")
    return {"task_id": task_id, "status": status}
