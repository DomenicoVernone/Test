from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from core.config import settings
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinical Twin — API Gateway",
    description="Autenticazione e gestione JWT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "api_gateway"}