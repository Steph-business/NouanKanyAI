"""Route HTTP du chat existant, conservant le contrat d'écho actuel."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatRequest(BaseModel):
    """Message soumis au Copilot par le client HTTP."""

    message: str = Field(..., description="Message textuel envoyé par l'opérateur")


@router.post("/chat", summary="Envoi d'un message au Copilot")
def chat(payload: ChatRequest) -> dict[str, str]:
    """Préserve le contrat historique du chat jusqu'au câblage applicatif."""
    return {"reply": f"Réception du message : {payload.message}", "status": "ok"}
