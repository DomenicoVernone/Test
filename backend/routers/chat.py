from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.llm_service import genera_risposta_medica
from core.security import get_current_user
from models.domain import User

router = APIRouter(prefix="/chat", tags=["Assistente AI"])

# Definizione del payload che arriverà da React
class ChatRequest(BaseModel):
    task_id: int
    message: str

@router.post("/", response_model=dict)
async def chat_con_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Riceve la domanda del medico, delega l'elaborazione al servizio LLM
    e restituisce la risposta contestualizzata.
    """
    risposta = await genera_risposta_medica(request.task_id, request.message)
    return {"response": risposta}