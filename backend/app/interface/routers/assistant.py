"""
app/interface/routers/assistant.py — Routeur FastAPI d'utilisation réelle du
Copilot IA (app/ai/), en remplacement du stub `chat.py` (qui ne fait
qu'échoer le message reçu).

Contrairement à `chat.py`, cette route passe par `IndustrialCopilot.ask()` :
mémoire conversationnelle multi-tours, contexte industriel réel (les mêmes
données démo que `GET /api/v1/machines`, voir app/services/demo_data.py),
et RAG/tool-calling optionnels (désactivés par défaut — aucune base
documentaire indexée ni vérification des outils faite à ce stade).

`AIGateway` gère lui-même son repli en mode simulation si GEMINI_API_KEY est
absent/factice (voir app/ai/gateway.py).
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.assistant import IndustrialCopilot
from app.ai.exceptions import AIGatewayError
from app.services.demo_data import load_demo_machine_state

router = APIRouter()

_copilot: Optional[IndustrialCopilot] = None


def _get_copilot() -> IndustrialCopilot:
    global _copilot
    if _copilot is None:
        _copilot = IndustrialCopilot()
    return _copilot


def _demo_machines_context() -> List[Dict[str, Any]]:
    """Adapte load_demo_machine_state() (clé `nom`) aux clés attendues par
    IndustrialContextBuilder.format_machines_context (`name`) — voir
    app/ai/context.py."""
    return [
        {
            "name": m.get("nom", m.get("machine_id", "Machine")),
            "status": m.get("status"),
            "power_kw": m.get("power_kw"),
            "temperature_c": m.get("temperature_c"),
            "vibration_hz": m.get("vibration_hz"),
        }
        for m in load_demo_machine_state()
    ]


class AssistantChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_rag: bool = False
    use_tools: bool = False


class AssistantChatResponse(BaseModel):
    response: str
    model_name: str
    latency_ms: float
    session_id: str


@router.post(
    "/assistant/chat",
    summary="Envoi d'un message au Copilot IA (RAG/mémoire/tool-calling)",
    description="Remplace le stub /chat par un vrai appel à IndustrialCopilot.ask().",
)
def assistant_chat(req: AssistantChatRequest) -> AssistantChatResponse:
    session_id = req.session_id or "demo-session"

    try:
        result = _get_copilot().ask(
            query=req.message,
            session_id=session_id,
            machines=_demo_machines_context(),
            use_rag=req.use_rag,
            use_tools=req.use_tools,
        )
    except AIGatewayError:
        return AssistantChatResponse(
            response="Désolé, l'assistant IA met trop de temps à répondre pour le moment. Réessayez dans quelques instants.",
            model_name="n/a",
            latency_ms=0.0,
            session_id=session_id,
        )

    return AssistantChatResponse(
        response=result.content,
        model_name=result.model_name,
        latency_ms=result.latency_ms,
        session_id=session_id,
    )
