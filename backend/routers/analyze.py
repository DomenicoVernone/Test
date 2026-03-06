"""
L'endpoint riceve il file .nii, lo salva fisicamente nel Volume Docker condiviso e 
crea un record PENDING nella tabella Tasks, rispondendo immediatamente al client senza bloccarsi.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.domain import Task, User
import shutil
import uuid
import os

from routers.auth import get_current_user 

router = APIRouter(prefix="/analyze", tags=["Orchestrator"])

# Puntiamo al Named Volume di Docker
UPLOAD_DIR = "/shared_data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_nifti_file(
    file: UploadFile = File(...), 
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
        status="PENDING",
        progress=0.0,
        owner_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 5. RISPOSTA IMMEDIATA
    return {
        "message": "File caricato nel volume condiviso. Elaborazione in coda.",
        "task_id": new_task.id,
        "status": new_task.status
    }