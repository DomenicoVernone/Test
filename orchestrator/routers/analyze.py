# orchestrator/routers/analyze.py
import hashlib
import os
import json

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.limiter import limiter
from models.domain import Task, User
from models.schemas import TaskResponse
from core.security import get_current_user, require_admin
from services.pipeline import run_full_pipeline

router = APIRouter(prefix="/analyze", tags=["Orchestrator"])

ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}


def _validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Modello non valido. Valori accettati: {sorted(ALLOWED_MODELS)}"
        )
    return model_name


async def _validate_mri_file(file: UploadFile) -> bytes:
    if not file.filename.endswith(('.nii', '.nii.gz')):
        raise HTTPException(
            status_code=400,
            detail="Formato non supportato. Caricare solo file .nii o .nii.gz"
        )

    content = await file.read()

    if len(content) < 1024:
        raise HTTPException(
            status_code=422,
            detail="File troppo piccolo o vuoto"
        )

    # gzip magic bytes (covers .nii.gz)
    is_gzip = content[:2] == b'\x1f\x8b'
    # NIfTI1 uncompressed magic at offset 344
    is_nifti1 = (
        len(content) > 348 and
        content[344:348] in (b'ni1\x00', b'n+1\x00')
    )
    # NIfTI2 uncompressed magic at offset 4
    is_nifti2 = (
        len(content) > 8 and
        content[4:8] in (b'ni2\x00', b'n+2\x00')
    )

    if not (is_gzip or is_nifti1 or is_nifti2):
        raise HTTPException(
            status_code=422,
            detail="Il file non è un NIfTI valido (.nii / .nii.gz)"
        )

    return content


@router.post("/", response_model=dict)
@limiter.limit("3/minute")
async def upload_nifti_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_model_name(model_name)
    file_content = await _validate_mri_file(file)

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
            # Race condition tra scrittura inference_engine e questa lettura
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


@router.delete("/admin/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Elimina qualsiasi task. Solo admin."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task non trovato")
    db.delete(task)
    db.commit()
