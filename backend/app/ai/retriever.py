"""
app/ai/retriever.py — Moteurs de recherche documentaire avancés (Hybride Dense + BM25, Reranker & Cache).

Fournit les interfaces et l'implémentation complète pour la recherche multi-collections,
le calcul d'embeddings, la fusion de scores et la mise en cache LRU.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.ai.citations import Citation, SourceCitationFormatter
from app.ai.document_processor import DocumentCollection, SmartTextChunker
from app.ai.embeddings import BaseEmbedder, MockEmbedder
from app.ai.query_cache import RAGQueryCache
from app.ai.reranker import BaseReranker, SemanticReranker
from app.ai.types import DocumentChunk, RetrievalResult
from app.ai.vector_store import BaseVectorStore, InMemoryVectorStore

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
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Recherche les segments documentaires les plus pertinents pour une requête donnée.

        :param query: Requête utilisateur ou question technique.
        :param top_k: Nombre maximal d'extraits à retourner.
        :param collection: Filtrage par collection documentaire.
        :param filters: Critères de filtrage par métadonnées.
        :return: Liste ordonnée de `DocumentChunk`.
        """
        pass

    def retrieve_with_metadata(
        self,
        query: str,
        top_k: int = 3,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """
        Effectue une recherche et encapsule le résultat dans un objet typé `RetrievalResult`.
        """
        chunks = self.retrieve(query, top_k=top_k, collection=collection, filters=filters)
        return RetrievalResult(
            query=query,
            chunks=chunks,
            total_found=len(chunks),
        )


class HybridRetriever(BaseRetriever):
    """
    Moteur de recherche hybride (Vectoriel + BM25) avec Reranking et Cache intégrés.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        embedder: Optional[BaseEmbedder] = None,
        reranker: Optional[BaseReranker] = None,
        query_cache: Optional[RAGQueryCache] = None,
        chunker: Optional[SmartTextChunker] = None,
        default_alpha: float = 0.6,
    ) -> None:
        """
        Initialise le moteur de recherche hybride.

        :param vector_store: Base vectorielle (InMemory, pgvector ou Qdrant).
        :param embedder: Générateur d'embeddings (Gemini ou Mock).
        :param reranker: Algorithme de réordonnancement.
        :param query_cache: Cache des requêtes.
        :param chunker: Découpeur intelligent.
        :param default_alpha: Poids dense vs sparse (0.6 = 60% vecteur, 40% BM25).
        """
        self.vector_store = vector_store or InMemoryVectorStore()
        self.embedder = embedder or MockEmbedder()
        self.reranker = reranker or SemanticReranker()
        self.query_cache = query_cache or RAGQueryCache()
        self.chunker = chunker or SmartTextChunker()
        self.default_alpha = default_alpha
        logger.debug("[HybridRetriever] Initialisé avec moteur hybride.")

    def ingest_document(
        self,
        document_id: str,
        content: str,
        collection: str = DocumentCollection.DOCUMENTATION_NOUANKANY.value,
        title: Optional[str] = None,
        source: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Ingère un document : découpage en chunks, calcul d'embeddings et indexation hybride.

        :param document_id: Identifiant unique du document.
        :param content: Texte brut ou markdown.
        :param collection: Collection cible (ISO 50001, ADEME, IoT, etc.).
        :param title: Titre du document.
        :param source: Chemin source ou URL.
        :param extra_metadata: Métadonnées additionnelles.
        :return: Liste des `DocumentChunk` créés et indexés.
        """
        # 1. Découpage intelligent
        chunks = self.chunker.chunk_text(
            text=content,
            document_id=document_id,
            collection=collection,
            title=title,
            source=source,
            extra_metadata=extra_metadata,
        )
        if not chunks:
            return []

        # 2. Génération des embeddings
        texts_to_embed = [c.content for c in chunks]
        embeddings = self.embedder.embed_documents(texts_to_embed)

        # 3. Indexation dans le vector store
        self.vector_store.add_chunks(chunks, embeddings)

        # 4. Invalidation du cache pour garantir la fraîcheur
        self.query_cache.clear()
        return chunks

    def add_document(self, chunk: DocumentChunk) -> None:
        """Ajoute directement un DocumentChunk à l'index vectoriel."""
        emb = self.embedder.embed_documents([chunk.content])
        self.vector_store.add_chunks([chunk], emb)
        self.query_cache.clear()

    def delete_document(self, document_id: str) -> int:
        """Supprime un document et ses chunks de l'index (mise à jour incrémentale)."""
        deleted_count = self.vector_store.delete_document(document_id)
        if deleted_count > 0:
            self.query_cache.clear()
        return deleted_count

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Exécute le pipeline complet de recherche :
        1. Consultation du Cache LRU
        2. Calcul de l'embedding de la requête
        3. Recherche Hybride (Cosinus + BM25)
        4. Reranking sémantique
        5. Mise en cache et retour des résultats
        """
        if not query or not query.strip():
            return []

        # 1. Vérification du cache
        cached = self.query_cache.get(query, collection=collection, top_k=top_k, filters=filters)
        if cached is not None:
            return cached

        # 2. Embedding de la requête
        query_emb = self.embedder.embed_query(query)

        # 3. Recherche hybride (on demande plus de candidats pour le reranking)
        candidate_count = max(top_k * 3, 10)
        candidates_with_scores = self.vector_store.search_hybrid(
            query_embedding=query_emb,
            query_text=query,
            top_k=candidate_count,
            alpha=self.default_alpha,
            collection=collection,
            filters=filters,
        )
        candidates = [chunk for chunk, _ in candidates_with_scores]

        # 4. Reranking sémantique
        reranked = self.reranker.rerank(query=query, chunks=candidates, top_k=top_k)

        # 5. Enregistrement en cache
        self.query_cache.set(
            query=query,
            chunks=reranked,
            collection=collection,
            top_k=top_k,
            filters=filters,
        )

        return reranked

    def get_citations(self, chunks: List[DocumentChunk]) -> List[Citation]:
        """Génère les objets de citation à partir des chunks retournés."""
        return SourceCitationFormatter.extract_citations(chunks)

    def count(self, collection: Optional[str] = None) -> int:
        """Nombre total de documents indexés."""
        return self.vector_store.count(collection)


# Alias de compatibilité
InMemoryRetriever = HybridRetriever
