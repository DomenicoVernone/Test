from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import engine, Base
from routers import auth, analyze

# 1. Inizializzazione del Database
# Crea fisicamente le tabelle (come la tabella users) nel file SQLite se non esistono
Base.metadata.create_all(bind=engine)

# 2. Inizializzazione dell'applicazione FastAPI
app = FastAPI(
    title="Clinical Twin API",
    description="Gateway asincrono per l'analisi clinica di risonanze magnetiche",
    version="1.0.0"
)

# 3. Configurazione CORS (Fondamentale per far comunicare React e FastAPI)
# Autorizziamo esplicitamente le porte usate dal nostro frontend Vite/Docker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Registrazione dei Router (I nostri moduli separati)
app.include_router(auth.router)
app.include_router(analyze.router)

@app.get("/")
def read_root():
    return {"message": "Clinical Twin API Gateway è operativo."}