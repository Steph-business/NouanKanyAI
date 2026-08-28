"""
app/interface/routers/chat.py — Routeur FastAPI pour les messages de l'assistant conversationnel.

Définit le contrat d'échange de messages et le point d'entrée de dialogue.
"""

from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatPayload(BaseModel):
    """
    Corps de requête pour envoyer un message à l'assistant.
    """
    message: str = Field(..., description="Message textuel envoyé par l'opérateur")


@router.post(
    "/chat",
    summary="Envoi d'un message à l'assistant Copilot",
    description="Traite une question de l'opérateur et retourne une réponse d'assistance opérationnelle.",
)
def chat_health(payload: ChatPayload) -> Dict[str, Any]:
    """
    Point d'entrée du chat de l'assistant.
    """
    return {
        "reply": f"Réception du message : {payload.message}",
        "status": "ok",
    }
