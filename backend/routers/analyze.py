# File: backend/routers/analyze.py
"""
Router per l'Orchestrazione Asincrona.
Gestisce unicamente le richieste HTTP, delegando l'elaborazione ai background tasks.
"""
import shutil
import uuid
import os
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from models.domain import Task, User
from models.schemas import TaskResponse  
from core.security import get_current_user
from services.pipeline import run_mock_nextflow

router = APIRouter(prefix="/analyze", tags=["Orchestrator"])

@router.post("/", response_model=dict)
async def upload_nifti_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    model_name: str = Form(...),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint per l'upload del file NIfTI e l'avvio della pipeline asincrona."""
    if not file.filename.endswith(('.nii', '.nii.gz')):
        raise HTTPException(status_code=400, detail="Formato non supportato. Caricare solo .nii o .nii.gz")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.NIFTI_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore I/O Volume Condiviso: {str(e)}")

    new_task = Task(
        filename=unique_filename,
        model_name=model_name,
        status="PENDING",
        progress=0.0,
        owner_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Il task in background gestirà SIA Nextflow CHE l'inferenza R
    background_tasks.add_task(
        run_mock_nextflow, 
        task_id=new_task.id, 
        model_name=model_name
    )

    return {
        "message": "File caricato. Elaborazione in coda.",
        "task_id": new_task.id,
        "status": new_task.status
    }

@router.get("/", response_model=list[TaskResponse])
async def get_medico_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restituisce lo storico task dell'utente (Tipizzato con Pydantic)."""
    return db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint di Polling Puro (Sola Lettura).
    Legge lo stato dal DB. Se completato, recupera il JSON calcolato dal task in background.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato o non autorizzato")

    # Se la pipeline (Nextflow + R) è ancora in corso
    if task.status in ["PENDING", "PROCESSING", "ANALYZING_R"]:
        return {"status": task.status, "message": "Elaborazione in corso...", "progress": task.progress}

    # Se il background task ha finito TUTTO con successo
    if task.status == "COMPLETED":
        result_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
        
        # CONTROLLO ANTI-RACE CONDITION DOCKER
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                dati_json = json.load(f)
                # Assicuriamoci di iniettare lo status "COMPLETED" dentro il payload per React
                dati_json["status"] = "COMPLETED"
                return dati_json
        else:
            # TRUCCO: Il database ha finito, ma il file system Docker è in ritardo.
            # Diciamo al frontend che stiamo ancora elaborando, così riproverà tra 1 secondo!
            return {"status": "PROCESSING", "message": "Sincronizzazione disco in corso...", "progress": 99.0}
        
    if task.status == "ERROR":
        return {"status": "ERROR", "message": "La pipeline ha subito un arresto anomalo."}

    return {"status": task.status}


@router.get("/nifti/{task_id}/volume.nii.gz")
async def get_nifti_file(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restituisce il file NIfTI per il Viewer 3D."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")

    file_path = os.path.join(settings.NIFTI_DIR, task.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File NIfTI non trovato sul disco")

    return FileResponse(file_path, media_type="application/gzip", filename=task.filename)