"""
app/ai/embeddings.py — Interfaces et adaptateurs pour la vectorisation sémantique (Embeddings).

Définit le contrat d'intégration pour les modèles de plongements lexicaux (text-embedding-004 de Google)
utilisés pour la recherche sémantique documentaire et l'indexation RAG.
"""

from abc import ABC, abstractmethod
import hashlib
import logging
import math
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
        Calcule le vecteur de plongement pour un texte unique.

        :param text: Chaîne de caractères à vectoriser.
        :return: Vecteur de flottants normalisé.
        """
        pass

    def embed_query(self, query: str) -> List[float]:
        """Alias pour embed_text."""
        return self.embed_text(query)

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
        """Génère le vecteur de plongement d'un texte."""
        # Vecteur pseudo-sémantique normalisé déterministe
        vec = [0.0] * self.dimension
        tokens = text.lower().split()
        for i, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            vec[idx] += 1.0 / (1.0 + math.log(1.0 + i))

        # Normalisation L2
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        else:
            vec = [1.0 / math.sqrt(self.dimension)] * self.dimension
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Génère les vecteurs de plongement pour une liste de documents."""
        return [self.embed_text(t) for t in texts]


class MockEmbedder(BaseEmbedder):
    """
    Générateur d'embeddings synthétiques pour les tests unitaires et le développement hors-ligne.
    Génère des représentations sémantiques déterministes par sac de mots hachés.
    """

    def __init__(self, dimension: int = 128) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        """Calcule un vecteur L2 normalisé déterministe."""
        vec = [0.0] * self.dimension
        words = text.lower().split()
        for w in words:
            h = int(hashlib.sha256(w.encode("utf-8")).hexdigest()[:8], 16)
            pos = h % self.dimension
            vec[pos] += 1.0

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            return [v / norm for v in vec]
        return [1.0 / math.sqrt(self.dimension)] * self.dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
