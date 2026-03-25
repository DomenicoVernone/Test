# File: llm_service/routers/chat.py
#
# Router FastAPI per l'endpoint di conversazione clinica.
# Riceve il messaggio del medico e lo storico della conversazione,
# delega la generazione della risposta a llm_service.genera_risposta_medica.

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.security import get_current_user
from services.llm_service import genera_risposta_medica

router = APIRouter(prefix="/chat", tags=["Assistente AI"])


class ChatMessage(BaseModel):
    role: str    # "user" o "assistant"
    content: str


class ChatRequest(BaseModel):
    task_id: int
    message: str
    history: List[ChatMessage] = []


@router.post("/", response_model=dict)
async def chat_con_ai(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    risposta = await genera_risposta_medica(
        task_id=request.task_id,
        messaggio_medico=request.message,
        history=[{"role": m.role, "content": m.content} for m in request.history],
    )
    return {"response": risposta}