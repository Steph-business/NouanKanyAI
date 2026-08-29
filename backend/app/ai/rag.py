"""
app/ai/rag.py — Pipeline de génération augmentée par la recherche (Retrieval-Augmented Generation).

Définit les interfaces et points d'orchestration liant le moteur de recherche documentaire multi-collections
(HybridRetriever), la construction de prompt (PromptBuilder) et l'inférence LLM (AIGateway).
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Union

from app.ai.citations import Citation, SourceCitationFormatter
from app.ai.document_processor import DocumentCollection
from app.ai.exceptions import RAGRetrievalError
from app.ai.gateway import AIGateway
from app.ai.prompt_builder import PromptBuilder
from app.ai.retriever import BaseRetriever, HybridRetriever
from app.ai.types import AIResponse, DocumentChunk

logger = logging.getLogger("nouankany.ai")


class BaseRAGPipeline(ABC):
    """
    Interface abstraite pour les pipelines RAG industriels.
    """

    @abstractmethod
    def run(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        top_k: int = 3,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_citations: bool = True,
    ) -> AIResponse:
        """
        Exécute le cycle complet : Recherche -> Augmentation -> Génération -> Citations.

        :param query: Requête technique de l'utilisateur.
        :param industrial_context: Contexte usine temps réel optionnel.
        :param top_k: Nombre d'extraits documentaires à injecter.
        :param collection: Filtrage par collection documentaire.
        :param filters: Filtres de recherche documentaire.
        :param include_citations: Si True, ajoute les notes de bas de page et citations dans la réponse.
        :return: Réponse typée `AIResponse`.
        """
        pass


class IndustrialRAGPipeline(BaseRAGPipeline):
    """
    Pipeline RAG industriel complet multi-collections pour NouanKanyAI.
    """

    def __init__(
        self,
        gateway: Optional[AIGateway] = None,
        retriever: Optional[BaseRetriever] = None,
        prompt_builder: Optional[PromptBuilder] = None,
    ) -> None:
        """
        Initialise le pipeline RAG industriel.

        :param gateway: Passerelle LLM Gemini.
        :param retriever: Moteur de recherche hybride (Dense + BM25).
        :param prompt_builder: Constructeur dynamique de prompts.
        """
        self.gateway = gateway or AIGateway()
        self.retriever = retriever or HybridRetriever()
        self.prompt_builder = prompt_builder or PromptBuilder()
        logger.debug("[IndustrialRAGPipeline] Pipeline RAG multi-collections opérationnel.")

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
        Permet l'ingestion directe d'un document dans le pipeline RAG.
        """
        if isinstance(self.retriever, HybridRetriever):
            return self.retriever.ingest_document(
                document_id=document_id,
                content=content,
                collection=collection,
                title=title,
                source=source,
                extra_metadata=extra_metadata,
            )
        return []

    def run(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        top_k: int = 3,
        collection: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_citations: bool = True,
    ) -> AIResponse:
        """
        Exécute la recherche documentaire, formate les extraits et interroge le LLM.
        """
        try:
            # 1. Recherche hybride des extraits pertinents (Vectoriel + BM25 + Rerank)
            chunks: List[DocumentChunk] = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                collection=collection,
                filters=filters,
            )

            # 2. Formatage des extraits documentaires pour le prompt
            rag_text = SourceCitationFormatter.format_sources_for_prompt(chunks)

            # 3. Assemblage du message enrichi
            messages = self.prompt_builder.create_chat_messages(
                query=query,
                industrial_context=industrial_context,
                rag_context=rag_text if rag_text else None,
            )

            # 4. Inférence LLM
            system_inst = self.prompt_builder.build_system_instruction()
            response = self.gateway.chat(
                messages=messages,
                system_instruction=system_inst,
            )

            # 5. Enrichissement de la réponse avec les citations et références
            citations = SourceCitationFormatter.extract_citations(chunks)
            if include_citations and citations:
                footnotes = SourceCitationFormatter.format_footnotes(citations)
                enriched_content = f"{response.content}{footnotes}"
                return AIResponse(
                    content=enriched_content,
                    model_name=response.model_name,
                    finish_reason=response.finish_reason,
                    latency_ms=response.latency_ms,
                    usage_tokens=response.usage_tokens,
                    tool_calls=response.tool_calls,
                    request_id=response.request_id,
                    raw_response={"citations": [c.model_dump() for c in citations]},
                )

            return response

        except Exception as e:
            logger.error(f"[IndustrialRAGPipeline] Erreur lors de l'exécution RAG : {e}")
            raise RAGRetrievalError(
                f"Échec du traitement RAG : {str(e)}", details={"query": query}
            ) from e
