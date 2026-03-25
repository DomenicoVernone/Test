# orchestrator/routers/analyze.py
#
# Endpoint HTTP per la gestione dei task di analisi.
# Riceve il file NIfTI, crea il task nel database e delega
# l'elaborazione a pipeline.py tramite background task FastAPI.
# Espone anche gli endpoint di polling e download NIfTI per il frontend.

import hashlib
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
from services.pipeline import run_full_pipeline

router = APIRouter(prefix="/analyze", tags=["Orchestrator"])


@router.post("/", response_model=dict)
async def upload_nifti_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(('.nii', '.nii.gz')):
        raise HTTPException(
            status_code=400,
            detail="Formato non supportato. Caricare solo file .nii o .nii.gz"
        )

    file_content = await file.read()

    # L'hash MD5 del contenuto garantisce che la stessa risonanza produca
    # sempre lo stesso filename — Nextflow può così sfruttare la cache -resume
    file_hash = hashlib.md5(file_content).hexdigest()[:8]
    unique_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(settings.NIFTI_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore scrittura volume condiviso: {str(e)}")

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

    background_tasks.add_task(run_full_pipeline, task_id=new_task.id, model_name=model_name)

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
    """Restituisce lo storico task dell'utente autenticato, ordinato per data."""
    return db.query(Task).filter(
        Task.owner_id == current_user.id
    ).order_by(Task.created_at.desc()).all()


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint di polling: restituisce lo stato del task e, se completato,
    il JSON con diagnosi, UMAP e feature anomale prodotto dall'inference_engine.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato o non autorizzato")

    if task.status in ["PENDING", "PROCESSING", "ANALYZING_R"]:
        return {
            "status": task.status,
            "message": "Elaborazione in corso...",
            "progress": task.progress
        }

    if task.status == "COMPLETED":
        result_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                result = json.load(f)
                result["status"] = "COMPLETED"
                return result
        else:
            # Il file JSON non è ancora visibile sul volume — race condition
            # tra la scrittura dell'inference_engine e questa lettura
            return {
                "status": "PROCESSING",
                "message": "Sincronizzazione disco in corso...",
                "progress": 99.0
            }

    if task.status == "ERROR":
        return {"status": "ERROR", "message": "La pipeline ha subito un arresto anomalo."}

    return {"status": task.status}


@router.get("/nifti/{task_id}/volume.nii.gz")
async def get_nifti_file(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restituisce il file NIfTI associato al task per il viewer 3D del frontend."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")

    file_path = os.path.join(settings.NIFTI_DIR, task.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File NIfTI non trovato sul disco")

    return FileResponse(
        file_path,
        media_type="application/gzip",
        filename=task.filename
    )