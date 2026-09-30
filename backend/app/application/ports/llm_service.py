"""Port abstrait vers un service de génération de langage."""

from abc import ABC, abstractmethod


class LLMService(ABC):
    """Contrat minimal de génération utilisé par les cas d'usage conversationnels."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Produit une réponse textuelle à partir d'une consigne."""
        raise NotImplementedError
