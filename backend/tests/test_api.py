# File: backend/tests/test_api.py
"""
Modulo di Test: API Endpoints (Livello Base)
Verifica la raggiungibilità e le risposte strutturali degli endpoint FastAPI.

Nota Architetturale: Utilizziamo TestClient di FastAPI per simulare le richieste HTTP
in memoria, garantendo esecuzioni istantanee senza occupare porte di rete.
"""
from fastapi.testclient import TestClient
# Assumiamo che la tua app FastAPI sia definita in main.py come 'app'
# Se si trova in un file diverso (es. api.py), modifica questa riga di conseguenza
from main import app 

# Inizializzazione del client di test isolato
client = TestClient(app)

def test_health_check_endpoint():
    """
    Verifica che l'endpoint root (o di health check) risponda correttamente.
    Implementa il pattern isolato Arrange-Act-Assert.
    """
    # --- ARRANGE (Prepara) ---
    # Definiamo l'endpoint. Se la tua app non ha un endpoint "/", 
    # sostituiscilo con uno semplice che sai esistere (es. "/api/status")
    endpoint_url = "/"

    # --- ACT (Agisci) ---
    # Eseguiamo la richiesta GET simulata, esattamente come farebbe il browser
    response = client.get(endpoint_url)

    # --- ASSERT (Verifica) ---
    # 1. Verifichiamo che il server non restituisca errori (Status 200 OK)
    assert response.status_code == 200, f"Errore: status code inatteso {response.status_code}"

    # 2. Verifichiamo che il payload sia formattato correttamente come JSON
    data = response.json()
    assert isinstance(data, dict), "Errore: la risposta non è un dizionario JSON valido"