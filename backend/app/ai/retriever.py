"""
app/ai/retriever.py — Interfaces et moteurs de recherche documentaire (Information Retrieval).

Définit les contrats d'abstraction pour la recherche de passages pertinents (chunks)
dans une base de connaissances documentaire (manuels d'usines, guides de délestage, normes ISO 50001).
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional
from app.ai.types import DocumentChunk, RetrievalResult

logger = logging.getLogger("nouankany.ai")


class BaseRetriever(ABC):
    """
    Interface abstraite pour tous les moteurs de recherche documentaire (RAG).
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Recherche les segments documentaires les plus pertinents pour une requête donnée.

        :param query: Requête utilisateur ou question technique.
        :param top_k: Nombre maximal d'extraits à retourner.
        :param filters: Critères de filtrage par métadonnées (ex: équipement, catégorie).
        :return: Liste ordonnée de `DocumentChunk`.
        """
        pass

    def retrieve_with_metadata(
        self,
        query: str,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """
        Effectue une recherche et encapsule le résultat dans un objet typé `RetrievalResult`.

        :param query: Question de recherche.
        :param top_k: Nombre d'extraits.
        :param filters: Filtres optionnels.
        :return: Instance `RetrievalResult`.
        """
        chunks = self.retrieve(query, top_k=top_k, filters=filters)
        return RetrievalResult(
            query=query,
            chunks=chunks,
            total_found=len(chunks),
        )


class InMemoryRetriever(BaseRetriever):
    """
    Moteur de recherche documentaire en mémoire pour les tests et la validation architecturale.
    """

    def __init__(self, initial_documents: Optional[List[DocumentChunk]] = None) -> None:
        self._documents: List[DocumentChunk] = initial_documents or []
        logger.debug(
            f"[InMemoryRetriever] Initialisé avec {len(self._documents)} documents."
        )

    def add_document(self, chunk: DocumentChunk) -> None:
        """Ajoute un extrait documentaire à la collection."""
        self._documents.append(chunk)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Recherche par correspondance de mots-clés simple (point d'extension pour vectoriel)."""
        if not self._documents:
            return []

        query_terms = set(query.lower().split())
        scored: List[tuple[DocumentChunk, float]] = []

        for doc in self._documents:
            # Filtrage par métadonnées si demandé
            if filters:
                match = all(doc.metadata.get(k) == v for k, v in filters.items())
                if not match:
                    continue

            content_lower = doc.content.lower()
            overlap = sum(1 for term in query_terms if term in content_lower)
            score = float(overlap) / max(len(query_terms), 1)
            scored.append((doc, score))

        # Tri décroissant par score
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]
