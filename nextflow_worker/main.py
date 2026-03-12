from fastapi import FastAPI, BackgroundTasks
import subprocess
import os

app = FastAPI()

def run_nextflow_pipeline(task_id: str):
    # Questo è il comando che gli autori lanciavano a mano!
    # Aggiungiamo -with-docker per dirgli di usare i container
    cmd = [
        "nextflow", "run", "nextflow/preprocessing.nf",
        "-with-docker",
        "--brain_segmenter", "fastsurfer" # Forziamo fastsurfer
    ]
    
    # Eseguiamo Nextflow asincronamente
    subprocess.run(cmd, cwd="/app")
    print(f"Task {task_id} completato dal Worker Nextflow!")

@app.post("/start_preprocessing/{task_id}")
async def start_preprocessing(task_id: str, background_tasks: BackgroundTasks):
    # Diciamo al worker di iniziare a lavorare in background
    background_tasks.add_task(run_nextflow_pipeline, task_id)
    return {"status": "accepted", "message": f"Nextflow avviato per il task {task_id}"}