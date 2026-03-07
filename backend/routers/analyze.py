"""
L'endpoint riceve il file .nii, lo salva fisicamente nel Volume Docker condiviso e 
crea un record PENDING nella tabella Tasks, rispondendo immediatamente al client senza bloccarsi.
"""
# File: backend/routers/analyze.py

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from core.database import get_db
from models.domain import Task, User
from services.pipeline import run_mock_nextflow
from services.inference import InferenceOrchestrator  # Il nostro nuovo ponte verso R
import shutil
import uuid
import os
import json 

from routers.auth import get_current_user 

router = APIRouter(prefix="/analyze", tags=["Orchestrator"])

# Puntiamo al Named Volume di Docker
UPLOAD_DIR = "/shared_data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_nifti_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    model_name: str = Form(...),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. CONTROLLO FORMATO
    if not file.filename.endswith('.nii') and not file.filename.endswith('.nii.gz'):
        raise HTTPException(status_code=400, detail="Formato non supportato. Caricare solo .nii o .nii.gz")

    # 2. NOME UNICO (Anti-collisione)
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. SALVATAGGIO NEL VOLUME CONDIVISO DOCKER
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel salvataggio: {str(e)}")

    # 4. CREAZIONE TASK NEL DATABASE
    new_task = Task(
        filename=unique_filename,
        model_name=model_name,  # Salviamo la scelta del modello direttamente nel Task
        status="PENDING",
        progress=0.0,
        owner_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 5. LANCIO DELLA PIPELINE IN BACKGROUND 
    background_tasks.add_task(run_mock_nextflow, new_task.id, unique_filename, UPLOAD_DIR, model_name)

    # 6. RISPOSTA IMMEDIATA
    return {
        "message": "File caricato. Elaborazione in coda.",
        "task_id": new_task.id,
        "status": new_task.status
    }

@router.get("/")
async def get_medico_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restituisce tutti i task (file caricati) appartenenti al medico loggato."""
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks

# ==========================================
# AGGIUNTA ARCHITETTURALE: Endpoint Polling
# ==========================================
@router.get("/status/{task_id}")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint per il polling asincrono di React.
    Se Nextflow ha finito, scatena l'inferenza R e restituisce il risultato.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato o non autorizzato")

    if task.status in ["PENDING", "PROCESSING"]:
        return {"status": task.status, "message": "Nextflow (FastSurfer) è in esecuzione...", "progress": task.progress}

    # Il "ponte" verso R scatta solo in questo esatto istante
    if task.status == "NEXTFLOW_COMPLETED":
        try:
            orchestrator = InferenceOrchestrator()
            model_to_use = task.model_name

            # Deleghiamo al microservizio R
            inference_result = await orchestrator.trigger_r_inference(str(task_id), model_to_use)
            
            # Allineiamo lo stato di R a quello di React
            inference_result["status"] = "COMPLETED"
            
            # --- NOVITÀ: SALVATAGGIO DEL RISULTATO NEL VOLUME ---
            result_path = os.path.join(UPLOAD_DIR, f"result_{task_id}.json")
            with open(result_path, "w") as f:
                json.dump(inference_result, f)
            # ----------------------------------------------------
            
            # Aggiorniamo il DB con il successo
            task.status = "COMPLETED"
            db.commit()
            
            return inference_result
            
        except Exception as e:
            task.status = "ERROR"
            db.commit()
            return {"status": "ERROR", "message": f"Errore Inference Engine: {str(e)}"}

    # --- NOVITÀ: RECUPERO DATI SE IL TASK È GIÀ FINITO ---
    if task.status == "COMPLETED":
        result_path = os.path.join(UPLOAD_DIR, f"result_{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                saved_result = json.load(f)
            return saved_result # Restituisce i dati completi con plot_data!
        else:
            return {"status": "COMPLETED", "message": "L'analisi è terminata (dati grafici non più disponibili)."}
        
    if task.status == "ERROR":
        return {"status": "ERROR", "message": "L'analisi ha subito un arresto anomalo."}

    return {"status": task.status}

@router.get("/nifti/{task_id}")
async def get_nifti_file(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restituisce il file NIfTI originale associato a un task (per il Viewer 3D)."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")

    file_path = os.path.join(UPLOAD_DIR, task.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File NIfTI non trovato sul disco")

    return FileResponse(file_path, media_type="application/gzip", filename=task.filename)