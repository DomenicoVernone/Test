"""
L'endpoint riceve il file .nii, lo salva fisicamente nel Volume Docker condiviso e 
crea un record PENDING nella tabella Tasks, rispondendo immediatamente al client senza bloccarsi.
"""
# 1. MODIFICA: Aggiungi 'Form' alle importazioni di fastapi
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from models.domain import Task, User
from services.pipeline import run_mock_nextflow
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
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    model_name: str = Form(...),  # 2. MODIFICA: FastAPI ora si aspetta questa variabile testuale
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

    # 5. LANCIO DELLA PIPELINE IN BACKGROUND 
    # 3. MODIFICA: Passiamo il 'model_name' alla funzione in background!
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
    # Cerca nel DB tutti i task dove l'owner_id corrisponde all'ID del medico
    # e li ordina dal più recente al più vecchio
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks