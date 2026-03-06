"""
Servizio di simulazione della pipeline di estrazione dati (Mock Nextflow).
Questo modulo simula i tempi di attesa dell'elaborazione delle immagini NIfTI
e genera un output CSV fittizio, aggiornando lo stato nel database.
"""
import asyncio
import os
import csv
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.domain import Task

async def run_mock_nextflow(task_id: int, filename: str, volume_dir: str):
    """
    Simula l'esecuzione asincrona di Nextflow.
    Essendo in background, dobbiamo aprire una nuova sessione DB indipendente.
    """
    db: Session = SessionLocal()
    try:
        # 1. Il sistema prende in carico il lavoro: PENDING -> PROCESSING
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        task.status = "PROCESSING"
        db.commit()

        # 2. Simuliamo l'attesa del calcolo intensivo (es. 10 secondi)
        # Qui in futuro ci sarà il comando reale: os.system("nextflow run ...")
        await asyncio.sleep(10) 

        # 3. Generiamo il "finto" CSV di output di cui parlava Donato
        # Simuliamo l'estrazione delle feature cerebrali
        output_filename = f"features_{task_id}.csv"
        output_path = os.path.join(volume_dir, output_filename)
        
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ROI", "Volume", "Spessore_Corticale"]) # Intestazioni
            writer.writerow(["Ippocampo", "3500.5", "2.8"])
            writer.writerow(["Amigdala", "1450.2", "3.1"])
            writer.writerow(["Corteccia_Frontale", "12050.0", "2.5"])

        # 4. Calcolo terminato: PROCESSING -> COMPLETED
        task.status = "COMPLETED"
        task.progress = 100.0
        db.commit()
        print(f"[NEXTFLOW MOCK] Task {task_id} completato con successo. CSV generato.")

    except Exception as e:
        task.status = "ERROR"
        db.commit()
        print(f"[NEXTFLOW MOCK] Errore critico nel task {task_id}: {e}")
    finally:
        # Chiudiamo sempre la sessione per non intasarla
        db.close()