from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from services.llm_service import genera_risposta_medica
from core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Assistente AI"])

class ChatMessage(BaseModel):
    role: str   # "user" o "assistant"
    content: str

class ChatRequest(BaseModel):
    task_id: int
    message: str
    history: List[ChatMessage] = []  # Storico dei turni precedenti della conversazione

@router.post("/", response_model=dict)
async def chat_con_ai(
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    risposta = await genera_risposta_medica(
        task_id=request.task_id,
        messaggio_medico=request.message,
        history=[{"role": m.role, "content": m.content} for m in request.history]
    )
    return {"response": risposta}