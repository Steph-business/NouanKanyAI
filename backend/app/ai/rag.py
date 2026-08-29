"""
app/ai/rag.py — Pipeline de génération augmentée par la recherche (Retrieval-Augmented Generation).

Définit les interfaces et points d'orchestration liant le moteur de recherche documentaire
(Retriever), la construction de prompt (PromptBuilder) et l'inférence LLM (AIGateway).
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional

from app.ai.exceptions import RAGRetrievalError
from app.ai.gateway import AIGateway
from app.ai.prompt_builder import PromptBuilder
from app.ai.retriever import BaseRetriever
from app.ai.types import AIResponse, DocumentChunk

logger = logging.getLogger("nouankany.ai")


class BaseRAGPipeline(ABC):
    """
    Interface abstraite pour les pipelines RAG.
    """

    @abstractmethod
    def run(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> AIResponse:
        """
        Exécute le cycle complet : Recherche -> Augmentation -> Génération.

        :param query: Requête technique de l'utilisateur.
        :param industrial_context: Contexte usine temps réel optionnel.
        :param top_k: Nombre d'extraits documentaires à injecter.
        :param filters: Filtres de recherche documentaire.
        :return: Réponse typée `AIResponse`.
        """
        pass


class IndustrialRAGPipeline(BaseRAGPipeline):
    """
    Pipeline RAG spécialisé pour le secteur industriel et énergétique.
    """

    def __init__(
        self,
        gateway: AIGateway,
        retriever: BaseRetriever,
        prompt_builder: Optional[PromptBuilder] = None,
    ) -> None:
        """
        Initialise le pipeline RAG.

        :param gateway: Passerelle LLM Gemini.
        :param retriever: Moteur de recherche documentaire.
        :param prompt_builder: Constructeur de prompts.
        """
        self.gateway = gateway
        self.retriever = retriever
        self.prompt_builder = prompt_builder or PromptBuilder()
        logger.debug("[IndustrialRAGPipeline] Initialisé.")

    def run(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> AIResponse:
        """
        Exécute la recherche documentaire, formate les extraits et interroge le LLM.
        """
        try:
            # 1. Récupération des extraits pertinents
            chunks: List[DocumentChunk] = self.retriever.retrieve(
                query=query, top_k=top_k, filters=filters
            )
            rag_text = ""
            if chunks:
                rag_blocks = [
                    f"--- Source: {c.metadata.get('source', c.document_id)} ---\n{c.content}"
                    for c in chunks
                ]
                rag_text = "\n\n".join(rag_blocks)

            # 2. Construction du prompt enrichi
            messages = self.prompt_builder.create_chat_messages(
                query=query,
                industrial_context=industrial_context,
                rag_context=rag_text if rag_text else None,
            )

            # 3. Génération via l'AI Gateway
            system_inst = self.prompt_builder.build_system_instruction()
            return self.gateway.chat(
                messages=messages,
                system_instruction=system_inst,
            )

        except Exception as e:
            logger.error(f"[IndustrialRAGPipeline] Erreur lors de l'exécution du pipeline RAG : {e}")
            raise RAGRetrievalError(
                f"Échec du traitement RAG : {str(e)}", details={"query": query}
            ) from e
