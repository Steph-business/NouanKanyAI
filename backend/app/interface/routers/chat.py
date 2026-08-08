from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatPayload(BaseModel):
    message: str


@router.post("/chat")
def chat_health(payload: ChatPayload):
    return {
        "reply": f"Réception du message : {payload.message}",
        "status": "ok",
    }
