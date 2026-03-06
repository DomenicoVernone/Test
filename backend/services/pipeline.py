"""
Servizio di simulazione della pipeline di estrazione dati (Mock Nextflow)
e orchestrazione dell'Inferenza tramite microservizio R (Plumber).
"""
import asyncio
import os
import csv
import requests  # <-- Nuova libreria per le chiamate HTTP
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.domain import Task

async def run_mock_nextflow(task_id: int, filename: str, volume_dir: str, model_name: str):
    db: Session = SessionLocal()
    try:
        print(f"🎯 [ORCHESTRATOR] Avvio Task {task_id}. Il medico ha scelto il modello: >>> {model_name} <<<")
        # 1. PENDING -> PROCESSING
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        task.status = "PROCESSING"
        db.commit()

        print(f"⚙️ [ORCHESTRATOR] Avvio estrazione feature per task {task_id}...")
        
        # 2. Simuliamo l'attesa di Nextflow
        await asyncio.sleep(5) 

        # 3. Generiamo il CSV nel Volume Condiviso
        output_filename = f"features_{task_id}.csv"
        output_path = os.path.join(volume_dir, output_filename)
        
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ROI", "Volume", "Spessore_Corticale"])
            writer.writerow(["Ippocampo", "3500.5", "2.8"])
            writer.writerow(["Amigdala", "1450.2", "3.1"])

        print(f"✅ [ORCHESTRATOR] CSV generato nel volume condiviso: {output_filename}")

        # --- IL PONTE DI COMANDO (Chiamata a Plumber) ---
        print(f"🚀 [ORCHESTRATOR] Invio richiesta di diagnosi al motore di inferenza (R)...")
        
        # L'URL interno di Docker (nome_servizio:porta_interna)
        inference_url = "http://inference:8000/predict"
        
        # Per ora diciamo che il medico aveva scelto la variante Comportamentale
        payload = {
            "task_id": task_id,
            "model_name": model_name
        }

        # Facciamo la chiamata POST a Plumber
        response = requests.post(inference_url, json=payload)
        
        if response.status_code == 200:
            risultato = response.json()
            diagnosi = risultato.get("diagnosi", "Errore di lettura")
            print(f"🎯 [INFERENCE RESULT] Il motore R ha sentenziato: >>> {diagnosi} <<<")
            
            # (Opzionale) Se hai una colonna 'result' nel database, salvalo qui:
            # task.result = diagnosi
        else:
            print(f"❌ [INFERENCE ERROR] Il container R ha risposto con errore: {response.text}")
        # ------------------------------------------------

        # 5. PROCESSING -> COMPLETED
        task.status = "COMPLETED"
        task.progress = 100.0
        db.commit()
        print(f"🏁 [ORCHESTRATOR] Task {task_id} completato e archiviato.")

    except Exception as e:
        task.status = "ERROR"
        db.commit()
        print(f"🚨 [ORCHESTRATOR] Errore critico nel task {task_id}: {e}")
    finally:
        db.close()