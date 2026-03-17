from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

TASKS_STATUS = {}

class NextflowTask(BaseModel):
    task_id: str
    input_path: str
    outdir: str

def run_nextflow_pipeline(task_id: str, input_path: str, outdir: str):
    # Usiamo la cartella isolata del volume condiviso passata dal backend
    os.makedirs(outdir, exist_ok=True)
    
    cmd = [
        "nextflow", "run", "/app/nextflow/preprocessing.nf",
        "-resume",
        "--image", input_path,
        "--outdir", outdir
    ]
    
    print(f"🔄 Avvio Nextflow per Task {task_id} nella directory del volume condiviso: {outdir}...")
    
    try:
        # cwd=outdir costringe Nextflow a lavorare e mettere il lucchetto qui
        subprocess.run(cmd, cwd=outdir, check=True)
        print(f"✅ Task {task_id} completato dal Worker Nextflow!")
        
        TASKS_STATUS[task_id] = "SUCCESS"
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRORE CRITICO: Nextflow fallito per il Task {task_id} con codice {e.returncode}")
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