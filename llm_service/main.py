from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers import chat

app = FastAPI(
    title="Clinical Twin — LLM Service",
    description="Assistente AI context-aware per la diagnosi differenziale",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "llm_service"}