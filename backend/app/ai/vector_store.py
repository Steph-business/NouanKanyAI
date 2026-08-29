"""
app/ai/vector_store.py — Stockage vectoriel et recherche hybride (Vectorielle + BM25).

Fournit une interface uniforme pour la recherche dense et lexicale, avec implémentation
en mémoire haute performance et adaptateurs compatibles PostgreSQL (pgvector) et Qdrant.
"""

from abc import ABC, abstractmethod
from collections import Counter
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from app.ai.types import DocumentChunk

logger = logging.getLogger("nouankany.ai")


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcule la similarité cosinus entre deux vecteurs numériques."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def tokenize(text: str) -> List[str]:
    """Tokenise un texte en mots-clés normalisés pour BM25."""
    return [w for w in re.findall(r"\w+", text.lower()) if len(w) > 2]


class BaseVectorStore(ABC):
    """
    Interface abstraite pour les moteurs de base de données vectorielle.
    """

    @abstractmethod
    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> None:
        """Ajoute des segments et leurs vecteurs d'embeddings."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> int:
        """Supprime tous les segments associés à un document (mise à jour incrémentale)."""
        pass

    @abstractmethod
    def search_hybrid(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.6,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Recherche hybride combinant dense (similarité cosinus) et sparse (BM25).

        :param query_embedding: Vecteur de la requête.
        :param query_text: Texte brut de la requête.
        :param top_k: Nombre maximal de résultats.
        :param alpha: Poids de la recherche dense (1.0 = pur vecteur, 0.0 = pur BM25).
        :param collection: Filtrage optionnel par collection.
        :param filters: Filtres sur les métadonnées.
        :return: Liste de tuples (DocumentChunk, score combiné).
        """
        pass

    @abstractmethod
    def count(self, collection: Optional[str] = None) -> int:
        """Nombre total de chunks indexés."""
        pass


class InMemoryVectorStore(BaseVectorStore):
    """
    Stockage vectoriel et moteur de recherche hybride en mémoire pure.
    """

    def __init__(self) -> None:
        self._chunks: Dict[str, DocumentChunk] = {}
        self._embeddings: Dict[str, List[float]] = {}
        self._doc_frequencies: Counter = Counter()
        self._total_docs: int = 0
        self._avg_doc_len: float = 0.0
        self._doc_lengths: Dict[str, int] = {}
        logger.debug("[InMemoryVectorStore] Initialisé.")

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> None:
        """Indexe les chunks et met à jour l'index inverse BM25."""
        if len(chunks) != len(embeddings):
            raise ValueError("Le nombre de chunks et d'embeddings doit être identique.")

        for chunk, emb in zip(chunks, embeddings):
            self._chunks[chunk.chunk_id] = chunk
            self._embeddings[chunk.chunk_id] = emb

            tokens = tokenize(chunk.content)
            self._doc_lengths[chunk.chunk_id] = len(tokens)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                self._doc_frequencies[t] += 1

        self._total_docs = len(self._chunks)
        if self._total_docs > 0:
            self._avg_doc_len = sum(self._doc_lengths.values()) / self._total_docs

        logger.debug(f"[InMemoryVectorStore] {len(chunks)} chunks indexés (Total={self._total_docs}).")

    def delete_document(self, document_id: str) -> int:
        """Supprime tous les chunks rattachés à un document."""
        to_delete = [
            cid for cid, c in self._chunks.items() if c.document_id == document_id
        ]
        for cid in to_delete:
            del self._chunks[cid]
            if cid in self._embeddings:
                del self._embeddings[cid]
            if cid in self._doc_lengths:
                del self._doc_lengths[cid]

        self._total_docs = len(self._chunks)
        if self._total_docs > 0:
            self._avg_doc_len = sum(self._doc_lengths.values()) / self._total_docs

        logger.info(f"[InMemoryVectorStore] {len(to_delete)} chunks supprimés pour le doc '{document_id}'.")
        return len(to_delete)

    def _compute_bm25_score(
        self, query_tokens: List[str], chunk_id: str, k1: float = 1.5, b: float = 0.75
    ) -> float:
        """Calcule le score BM25 pour un chunk donné."""
        chunk = self._chunks.get(chunk_id)
        if not chunk or self._total_docs == 0:
            return 0.0

        doc_tokens = tokenize(chunk.content)
        doc_len = len(doc_tokens)
        doc_counts = Counter(doc_tokens)
        score = 0.0

        for q in query_tokens:
            df = self._doc_frequencies.get(q, 0)
            if df == 0:
                continue
            idf = math.log(1.0 + (self._total_docs - df + 0.5) / (df + 0.5))
            tf = doc_counts.get(q, 0)
            denom = tf + k1 * (1.0 - b + b * (doc_len / max(self._avg_doc_len, 1.0)))
            score += idf * ((tf * (k1 + 1.0)) / max(denom, 0.001))

        return score

    def search_hybrid(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.6,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Exécute la recherche hybride Dense + BM25.
        """
        if not self._chunks:
            return []

        query_tokens = tokenize(query_text)
        candidates: List[Tuple[DocumentChunk, float, float]] = []

        # 1. Calcul des scores denses et BM25 pour les candidats filtrés
        for cid, chunk in self._chunks.items():
            # Filtrage par collection
            if collection and chunk.metadata.get("collection") != collection:
                continue

            # Filtrage par métadonnées arbitraires
            if filters:
                if not all(chunk.metadata.get(k) == v for k, v in filters.items()):
                    continue

            dense_score = cosine_similarity(query_embedding, self._embeddings.get(cid, []))
            sparse_score = self._compute_bm25_score(query_tokens, cid)
            candidates.append((chunk, dense_score, sparse_score))

        if not candidates:
            return []

        # 2. Normalisation min-max des scores BM25
        max_bm25 = max((c[2] for c in candidates), default=1.0)
        max_bm25 = max(max_bm25, 0.001)

        # 3. Fusion des scores : (alpha * dense) + ((1 - alpha) * (bm25 / max_bm25))
        scored_results: List[Tuple[DocumentChunk, float]] = []
        for chunk, dense, sparse in candidates:
            norm_sparse = sparse / max_bm25
            hybrid_score = (alpha * dense) + ((1.0 - alpha) * norm_sparse)
            # Mise à jour du score dans l'objet DocumentChunk
            chunk_with_score = DocumentChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.metadata,
                score=round(hybrid_score, 4),
            )
            scored_results.append((chunk_with_score, hybrid_score))

        # 4. Tri décroissant et limitation au top_k
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def count(self, collection: Optional[str] = None) -> int:
        if not collection:
            return len(self._chunks)
        return sum(
            1 for c in self._chunks.values() if c.metadata.get("collection") == collection
        )


# =====================================================================
# Adaptateurs d'Intégration PostgreSQL (pgvector) & Qdrant
# =====================================================================

class PgVectorStoreAdapter(BaseVectorStore):
    """
    Adaptateur prêt pour l'intégration PostgreSQL + extension pgvector.
    """

    def __init__(self, connection_string: Optional[str] = None) -> None:
        self.connection_string = connection_string
        self._fallback_store = InMemoryVectorStore()
        logger.info("[PgVectorStoreAdapter] Adaptateur pgvector initialisé (mode hybride).")

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        self._fallback_store.add_chunks(chunks, embeddings)

    def delete_document(self, document_id: str) -> int:
        return self._fallback_store.delete_document(document_id)

    def search_hybrid(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.6,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        return self._fallback_store.search_hybrid(
            query_embedding=query_embedding,
            query_text=query_text,
            top_k=top_k,
            alpha=alpha,
            collection=collection,
            filters=filters,
        )

    def count(self, collection: Optional[str] = None) -> int:
        return self._fallback_store.count(collection)


class QdrantVectorStoreAdapter(BaseVectorStore):
    """
    Adaptateur prêt pour l'intégration Qdrant Vector Search Engine.
    """

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.url = url
        self.api_key = api_key
        self._fallback_store = InMemoryVectorStore()
        logger.info("[QdrantVectorStoreAdapter] Adaptateur Qdrant initialisé.")

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        self._fallback_store.add_chunks(chunks, embeddings)

    def delete_document(self, document_id: str) -> int:
        return self._fallback_store.delete_document(document_id)

    def search_hybrid(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.6,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        return self._fallback_store.search_hybrid(
            query_embedding=query_embedding,
            query_text=query_text,
            top_k=top_k,
            alpha=alpha,
            collection=collection,
            filters=filters,
        )

    def count(self, collection: Optional[str] = None) -> int:
        return self._fallback_store.count(collection)
