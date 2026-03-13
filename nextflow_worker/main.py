from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess

app = FastAPI()

TASKS_STATUS = {}

class NextflowTask(BaseModel):
    task_id: str
    input_path: str
    outdir: str

def run_nextflow_pipeline(task_id: str, input_path: str, outdir: str):
    # Eseguiamo Nextflow passandogli il singolo file (--image) e la cartella di output (--outdir)
    cmd = [
        "nextflow", "run", "nextflow/preprocessing.nf",
        "-resume",  # Per abilitare il caching e non rifare tutto se già fatto
        "--image", input_path,
        "--outdir", outdir
    ]
    
    print(f"🔄 Avvio Nextflow per Task {task_id}...")
    
    try:
        subprocess.run(cmd, cwd="/app", check=True)
        print(f"✅ Task {task_id} completato dal Worker Nextflow!")
        
        TASKS_STATUS[task_id] = "SUCCESS"
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRORE CRITICO: Nextflow fallito per il Task {task_id} con codice {e.returncode}")
        
        # Segniamo il fallimento nel registro in modo che il Backend lo veda
        TASKS_STATUS[task_id] = "FAILED"

@app.post("/start_preprocessing")
async def start_preprocessing(task: NextflowTask, background_tasks: BackgroundTasks):
    # Appena riceviamo la richiesta, segniamo il task come RUNNING
    TASKS_STATUS[task.task_id] = "RUNNING"
    
    background_tasks.add_task(run_nextflow_pipeline, task.task_id, task.input_path, task.outdir)
    return {"status": "accepted", "message": f"Nextflow avviato per il task {task.task_id}"}

# 2. IL CAMPANELLO: Il Backend chiamerà questa rotta durante il polling
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    status = TASKS_STATUS.get(task_id, "UNKNOWN")
    return {"task_id": task_id, "status": status}