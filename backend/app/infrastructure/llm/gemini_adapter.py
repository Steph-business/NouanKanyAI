"""Adaptateur du gateway Gemini historique vers le port de génération LLM."""

import asyncio

from app.ai.gateway import AIGateway
from app.application.ports.llm_service import LLMService


class GeminiAdapter(LLMService):
    """Réutilise AIGateway et son fallback de simulation existant."""

    def __init__(self, gateway: AIGateway | None = None) -> None:
        self.gateway = gateway or AIGateway()

    async def generate(self, prompt: str) -> str:
        """Génère une réponse en déléguant l'appel bloquant au thread pool."""
        response = await asyncio.to_thread(self.gateway.generate_text, prompt)
        return response.content
