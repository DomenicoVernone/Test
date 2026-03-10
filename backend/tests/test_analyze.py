# File: backend/tests/test_analyze.py
"""
Modulo di Test: Router di Analisi e Orchestrazione.
Verifica l'intero ciclo di vita del NIfTI: Upload, Storico, Polling asincrono,
e gestione delle Race Condition tra Database e File System Docker.
"""
import io
import os
import tempfile
import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from core.config import settings 

from main import app
from core.security import get_current_user
from core.database import get_db
from models.domain import Task

# --- MOCKING GLOBALE DELLE DIPENDENZE ---
def mock_get_current_user():
    class MockUser:
        id = 1
        email = "medico@ospedale.it"
    return MockUser()

# Creiamo una finta sessione DB globale che possiamo manipolare dentro i test
mock_session = MagicMock()

def mock_get_db():
    yield mock_session

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db

client = TestClient(app)


# --- 1. TEST DI UPLOAD (Scrittura) ---

def test_upload_nifti_success():
    """Verifica il caricamento corretto di un file NIfTI."""
    fake_file = io.BytesIO(b"fake-nifti")
    files = {"file": ("paziente.nii.gz", fake_file, "application/gzip")}
    form_data = {"model_name": "HC_vs_bvFTD"}

    response = client.post("/analyze/", files=files, data=form_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"
    assert "task_id" in data

def test_upload_invalid_file_extension():
    """Verifica il blocco di formati non validi."""
    fake_file = io.BytesIO(b"testo")
    files = {"file": ("documento.txt", fake_file, "text/plain")}
    response = client.post("/analyze/", files=files, data={"model_name": "modello"})
    assert response.status_code == 400


# --- 2. TEST DELLO STORICO (Lettura) ---

def test_get_medico_tasks():
    """Verifica che l'endpoint restituisca la lista dei task del medico loggato."""
    # FIX: Aggiunti progress, created_at e updated_at per soddisfare la validazione Pydantic
    finto_task = Task(
        id=10, 
        filename="test.nii", 
        status="COMPLETED", 
        model_name="ModelloA", 
        owner_id=1,
        progress=100.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [finto_task]

    response = client.get("/analyze/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 10


# --- 3. TEST DEL POLLING E RACE CONDITION ---

def test_task_status_pending():
    """Verifica il polling quando la pipeline è ancora in corso."""
    finto_task = Task(id=1, status="ANALYZING_R", progress=50.0, owner_id=1)
    # Mockiamo la catena: query().filter().first()
    mock_session.query.return_value.filter.return_value.first.return_value = finto_task

    response = client.get("/analyze/status/1")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ANALYZING_R"
    assert response.json()["progress"] == 50.0

@patch("os.path.exists") # Intercettiamo la chiamata al file system
def test_task_status_docker_race_condition(mock_exists):
    """
    IL TEST PIÙ IMPORTANTE:
    Verifica che se il DB dice COMPLETED, ma il file JSON non è ancora fisicamente
    arrivato sul disco (ritardo Docker), il backend inganni il frontend
    dicendo "PROCESSING" per forzare un nuovo tentativo, evitando crash.
    """
    # 1. Il DB dice che ha finito
    finto_task = Task(id=1, status="COMPLETED", owner_id=1)
    mock_session.query.return_value.filter.return_value.first.return_value = finto_task
    
    # 2. Ma il disco dice che il file non esiste (Race Condition!)
    mock_exists.return_value = False

    response = client.get("/analyze/status/1")
    
    assert response.status_code == 200
    data = response.json()
    # Il backend intercetta il problema e degrada lo status a PROCESSING!
    assert data["status"] == "PROCESSING"
    assert data["progress"] == 99.0


# --- 4. TEST DEL DOWNLOAD NIFTI ---

# --- 4. TEST DEL DOWNLOAD NIFTI ---

def test_get_nifti_file():
    """Verifica il download fisico del file 3D per il visualizzatore."""
    # FIX: Creiamo un file temporaneo reale direttamente nella VERA cartella configurata
    filename = "test_temporaneo.nii.gz"
    file_path = os.path.join(settings.NIFTI_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(b"dati-3d-finti")

    # Istruiamo il finto DB a restituire il nome del file appena creato
    finto_task = Task(id=1, filename=filename, owner_id=1)
    mock_session.query.return_value.filter.return_value.first.return_value = finto_task

    # Effettuiamo la chiamata di download
    response = client.get("/analyze/nifti/1/volume.nii.gz")

    # Pulizia: cancelliamo il file per non sporcare il disco
    if os.path.exists(file_path):
        os.remove(file_path)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/gzip"