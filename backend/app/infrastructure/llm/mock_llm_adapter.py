"""Faux service LLM déterministe pour les tests et démos hors ligne."""

from app.application.ports.llm_service import LLMService


class MockLLMAdapter(LLMService):
    """Retourne un texte configuré sans appel externe."""

    def __init__(self, response: str = "Réponse de démonstration.") -> None:
        self.response = response

    async def generate(self, prompt: str) -> str:
        """Retourne une réponse déterministe au prompt reçu."""
        return self.response
