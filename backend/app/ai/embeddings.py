"""
app/ai/embeddings.py — Interfaces et adaptateurs pour la vectorisation sémantique (Embeddings).

Définit le contrat d'intégration pour les modèles de plongements lexicaux (text-embedding-004 de Google)
utilisés pour la recherche sémantique documentaire et l'indexation RAG.
"""

from abc import ABC, abstractmethod
import logging
import os
from typing import List, Optional

logger = logging.getLogger("nouankany.ai")


class BaseEmbedder(ABC):
    """
    Interface abstraite pour les services de calcul d'embeddings vectoriels.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Calcule le vecteur de plongement pour un texte unique (requête).

        :param text: Chaîne de caractères à vectoriser.
        :return: Vecteur de flottants normalisé.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Calcule les vecteurs de plongement pour un ensemble de documents.

        :param texts: Liste de textes à vectoriser.
        :return: Liste de vecteurs.
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionnalité des vecteurs générés."""
        pass


class GeminiEmbedder(BaseEmbedder):
    """
    Adaptateur pour le modèle text-embedding-004 de Google.
    Fournit un point d'extension complet pour l'indexation vectorielle.
    """

    DEFAULT_MODEL = "text-embedding-004"
    DEFAULT_DIMENSION = 768

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL,
        dimension: int = DEFAULT_DIMENSION,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self._dimension = dimension
        logger.debug(f"[GeminiEmbedder] Initialisé (model={model_name}, dim={dimension})")

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        """Génère le vecteur de plongement d'une requête."""
        if not self.api_key:
            # Mode simulation / fallback déterministe
            return [0.0] * self.dimension

        # Point d'extension pour appel REST Gemini Embedding
        # (Sera complété dans l'étape d'implémentation RAG)
        return [0.01] * self.dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Génère les vecteurs de plongement pour une liste de documents."""
        return [self.embed_text(t) for t in texts]


class MockEmbedder(BaseEmbedder):
    """
    Générateur d'embeddings synthétiques pour les tests unitaires et le développement hors-ligne.
    """

    def __init__(self, dimension: int = 128) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        # Vecteur pseudo-déterministe basé sur le hash du texte
        val = (abs(hash(text)) % 1000) / 1000.0
        return [val] * self._dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
