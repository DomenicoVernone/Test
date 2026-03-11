"""
Script di Load Testing per l'architettura Clinical Twin.
======================================================
Utilizza Locust per simulare chiamate concorrenti all'API Gateway.
Obiettivo: Dimostrare che FastAPI gestisce l'upload e il trigger di 
Nextflow senza bloccare l'Event Loop per gli altri utenti.

Prerequisiti: pip install locust
Esecuzione: locust -f scripts/locustfile.py --host=http://localhost:8000
"""

import os
import io
import uuid
from locust import HttpUser, task, between

class ClinicalTwinUser(HttpUser):
    # Tempo di attesa ottimizzato per non saturare l'Host locale
    wait_time = between(5.0, 15.0)
    
    # =====================================================================
    # CONFIGURAZIONE URL
    # =====================================================================
    REGISTER_URL = "/signup"   
    LOGIN_URL = "/login"         
    ANALYZE_URL = "/analyze"          
    STATUS_URL_PATTERN = "/analyze/status/999" 
    # =====================================================================
    
    def on_start(self):
        """Eseguito all'avvio: registra un utente UNIVOCO e fa il login per il JWT Token."""
        
        unique_suffix = uuid.uuid4().hex[:8]
        self.test_username = f"locust_tester_{unique_suffix}"
        self.test_password = "supersecretpassword123"
        
        with self.client.post(self.REGISTER_URL, json={
            "username": self.test_username,
            "password": self.test_password,
            "email": f"{self.test_username}@clinicaltwin.com"
        }, catch_response=True) as response:
            if response.status_code not in [200, 201]:
                response.failure(f"Registrazione fallita: {response.text}")
        
        response = self.client.post(self.LOGIN_URL, data={
            "grant_type": "password",
            "username": self.test_username,
            "password": self.test_password
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
            print(f"[SUCCESS] Login effettuato per {self.test_username}")
        else:
            self.headers = {}
            print(f"[ERROR] Impossibile ottenere il token per {self.test_username}. Status: {response.status_code}")

    @task(1)
    def test_status_polling(self):
        """Simula il polling continuo per un task."""
        if not self.headers:
            return

        with self.client.get(self.STATUS_URL_PATTERN, headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 404]: 
                response.success()
            else:
                response.failure(f"Errore nel polling: {response.status_code}")

    @task(3)
    def test_async_upload(self):
        """Simula l'upload di un file NIfTI fittizio per testare la non-bloccabilità."""
        if not self.headers:
            return

        dummy_nifti_content = b"0" * (1024 * 1024) 
        
        files = {
            'file': ('dummy_test.nii', io.BytesIO(dummy_nifti_content), 'application/octet-stream')
        }
        
        # FIX: Il payload viene inviato con un valore realistico ('champion')
        data_payload = {
            'model_name': 'champion' 
        }
        
        # FIX: Invio 'data_payload' sia come parametro query (params) che come form-data (data).
        # Questo garantisce che FastAPI trovi 'model_name' a prescindere da come è definito nel backend.
        with self.client.post(
            self.ANALYZE_URL, 
            params=data_payload, 
            data=data_payload, 
            files=files, 
            headers=self.headers, 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    json_resp = response.json()
                    if json_resp.get("status") in ["IN_PROGRESS", "PENDING", "COMPLETED"]:
                        response.success()
                    else:
                        response.failure(f"Status inatteso: {json_resp.get('status')}")
                except ValueError:
                    response.failure(f"Risposta non JSON dal server. Testo: {response.text}")
            elif response.status_code == 401:
                response.failure("Non autorizzato (Token mancante o invalido)")
            elif response.status_code == 422:
                response.failure(f"422 Validation Error: {response.text}")
            elif response.status_code == 400:
                response.failure(f"Errore di validazione input: {response.text}")
            elif response.status_code == 500:
                response.failure("500 Internal Server Error (Il DB SQLite è bloccato o le risorse host sono sature)")
            elif response.status_code == 502:
                response.failure("502 Bad Gateway (Il container FastAPI è crashato per esaurimento RAM/CPU)")
            else:
                response.failure(f"Upload fallito all'URL {self.ANALYZE_URL}: {response.status_code} - {response.text}")