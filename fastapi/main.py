import httpx
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Permettiamo al frontend di parlare con il backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In produzione metterai l'indirizzo specifico
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientRequest(BaseModel):
    patient_id: int

@app.post("/analyze")
async def start_analysis(payload: PatientRequest):
    # Magia di Docker: usiamo il nome del servizio "modello-r" invece di un IP!
    url_r = f"http://modello-r:8000/predict?id_paziente={payload.patient_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url_r)
        dati_da_r = response.json()
    
    return {
        "messaggio": "Risultato ottenuto dal modello R",
        "dati_clinici": dati_da_r
    }