"""
app/ai/reranker.py — Module de Reranking des passages documentaires (Cross-Scoring & Pertinence).

Réordonne et filtre les segments documentaires candidats issus de la recherche hybride
pour maximiser la précision des informations présentées au LLM.
"""

from abc import ABC, abstractmethod
import logging
import re
from typing import List, Optional
from app.ai.types import DocumentChunk

logger = logging.getLogger("nouankany.ai")


class BaseReranker(ABC):
    """
    Interface abstraite pour les algorithmes de reranking.
    """

    @abstractmethod
    def rerank(
        self,
        query: str,
        chunks: List[DocumentChunk],
        top_k: int = 3,
    ) -> List[DocumentChunk]:
        """
        Réordonne les chunks candidats selon leur pertinence croisée avec la requête.

        :param query: Requête de l'utilisateur.
        :param chunks: Liste de chunks candidats.
        :param top_k: Nombre maximal de chunks à retenir après reranking.
        :return: Liste réordonnée et filtrée de `DocumentChunk`.
        """
        pass


class SemanticReranker(BaseReranker):
    """
    Reranker sémantique hybride combinant similarité dense, exact-match de termes clés,
    pertinence des titres de section et pénalité de redondance.
    """

    def __init__(self, exact_match_boost: float = 0.25, title_match_boost: float = 0.20) -> None:
        self.exact_match_boost = exact_match_boost
        self.title_match_boost = title_match_boost

    def rerank(
        self,
        query: str,
        chunks: List[DocumentChunk],
        top_k: int = 3,
    ) -> List[DocumentChunk]:
        """
        Calcule un score affiné pour chaque chunk et réordonne.
        """
        if not chunks:
            return []

        query_lower = query.lower()
        query_terms = [w for w in re.findall(r"\w+", query_lower) if len(w) > 2]

        scored_chunks = []
        for chunk in chunks:
            base_score = chunk.score if chunk.score is not None else 0.5
            content_lower = chunk.content.lower()
            section_lower = str(chunk.metadata.get("section", "")).lower()
            title_lower = str(chunk.metadata.get("title", "")).lower()

            # 1. Bonus si la phrase exacte apparaît
            exact_phrase_bonus = self.exact_match_boost if query_lower in content_lower else 0.0

            # 2. Bonus si les termes de la requête sont dans le titre ou la section
            title_matches = sum(1 for t in query_terms if t in title_lower or t in section_lower)
            title_bonus = min(self.title_match_boost, title_matches * 0.10)

            # 3. Ratio de couverture des termes
            term_coverage = sum(1 for t in query_terms if t in content_lower) / max(len(query_terms), 1)

            final_score = base_score * 0.6 + term_coverage * 0.2 + exact_phrase_bonus + title_bonus
            final_score = min(1.0, max(0.0, final_score))

            reranked_chunk = DocumentChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.metadata,
                score=round(final_score, 4),
            )
            scored_chunks.append(reranked_chunk)

        # Tri décroissant par score affiné
        scored_chunks.sort(key=lambda c: c.score or 0.0, reverse=True)
        return scored_chunks[:top_k]
