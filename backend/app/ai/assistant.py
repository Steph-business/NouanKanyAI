"""
app/ai/assistant.py — Assistant Copilot industriel et orchestrateur de haut niveau.

Coordonne la passerelle LLM (AIGateway), le constructeur de contexte industriel
(IndustrialContextBuilder), les gabarits de prompts (PromptBuilder), la mémoire multi-niveaux
(ConversationMemoryManager), le registre d'outils (ToolRegistry) et les modules RAG.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.context import IndustrialContextBuilder
from app.ai.conversation import ConversationManager
from app.ai.gateway import AIGateway
from app.ai.memory import ConversationMemoryManager
from app.ai.prompt_builder import PromptBuilder
from app.ai.rag import BaseRAGPipeline
from app.ai.tools import ToolRegistry
from app.ai.types import AIResponse, GenerationConfig, MessageRole

logger = logging.getLogger("nouankany.ai")


class IndustrialCopilot:
    """
    Copilot IA expert en efficacité énergétique industrielle pour NouanKanyAI.
    Façade d'orchestration pour toutes les interactions conversationnelles intelligentes.
    """

    def __init__(
        self,
        gateway: Optional[AIGateway] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        context_builder: Optional[IndustrialContextBuilder] = None,
        conversation_manager: Optional[ConversationManager] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory_manager: Optional[ConversationMemoryManager] = None,
        rag_pipeline: Optional[BaseRAGPipeline] = None,
    ) -> None:
        """
        Initialise le Copilot industriel avec injection de dépendances.

        :param gateway: Passerelle LLM Gemini.
        :param prompt_builder: Constructeur d'instructions système et de messages.
        :param context_builder: Formateur de télémétrie industrielle temps réel.
        :param conversation_manager: Gestionnaire d'historique de sessions.
        :param tool_registry: Registre des outils métier (Function Calling).
        :param memory_manager: Gestionnaire de mémoire multi-niveaux (court/long terme).
        :param rag_pipeline: Pipeline de recherche documentaire RAG.
        """
        self.gateway = gateway or AIGateway()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.context_builder = context_builder or IndustrialContextBuilder()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.tool_registry = tool_registry or ToolRegistry.create_default_registry()
        self.memory_manager = memory_manager or ConversationMemoryManager()
        self.rag_pipeline = rag_pipeline

        logger.info("[IndustrialCopilot] Copilot opérationnel avec registre d'outils par défaut.")

    def ask(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        machines: Optional[List[Dict[str, Any]]] = None,
        alerts: Optional[List[Dict[str, Any]]] = None,
        current_hour: Optional[int] = None,
        use_rag: bool = False,
        use_tools: bool = False,
        config: Optional[GenerationConfig] = None,
    ) -> AIResponse:
        """
        Traite une requête utilisateur dans son contexte industriel, mémoriel et conversationnel.

        :param query: Question ou commande de l'opérateur / directeur d'usine.
        :param session_id: Identifiant de la session de chat.
        :param user_id: Identifiant de l'utilisateur.
        :param org_id: Identifiant de l'organisation.
        :param building_id: Identifiant du bâtiment / site industriel.
        :param machines: Données télémétriques des machines actuelles.
        :param alerts: Données des alertes et anomalies actives.
        :param current_hour: Heure d'analyse (CIE).
        :param use_rag: Si True et si le pipeline RAG est configuré, effectue une recherche documentaire.
        :param use_tools: Si True, expose les outils métier pour appel de fonction.
        :param config: Hyperparamètres de génération.
        :return: Réponse structurée `AIResponse`.
        """
        active_session = self.conversation_manager.get_or_create_session(session_id, user_id=user_id)
        sid = active_session.session_id

        # 1. Construction du contexte industriel temps réel
        industrial_ctx = self.context_builder.build_full_context(
            machines=machines,
            alerts=alerts,
            current_hour=current_hour,
        )

        # 2. Récupération de la mémoire pertinente (préférences, équipements, synthèses)
        memory_ctx = self.memory_manager.get_relevant_context_for_prompt(
            session_id=sid,
            user_id=user_id,
            org_id=org_id,
            building_id=building_id,
            query=query,
        )

        # 3. Recherche documentaire RAG optionnelle
        rag_context: Optional[str] = None
        if use_rag and self.rag_pipeline is not None:
            try:
                logger.debug(f"[IndustrialCopilot] Recherche RAG activée pour la requête : {query}")
            except Exception as e:
                logger.warning(f"[IndustrialCopilot] Échec partiel du RAG : {e}")

        # 4. Récupération de l'historique conversationnel court terme
        history = self.conversation_manager.get_history(sid, limit=10)

        # 5. Assemblage de la liste de messages enrichis
        messages = self.prompt_builder.create_chat_messages(
            query=query,
            conversation_history=history,
            industrial_context=industrial_ctx,
            memory_context=memory_ctx if memory_ctx else None,
            rag_context=rag_context,
        )

        # 6. Préparation des outils (Function Calling)
        tools_schema = self.tool_registry.get_gemini_schemas() if use_tools else None

        # 7. Génération via l'AI Gateway
        system_instruction = self.prompt_builder.build_system_instruction()
        response = self.gateway.chat(
            messages=messages,
            system_instruction=system_instruction,
            tools=tools_schema,
            config=config,
        )

        # 8. Persistance du tour dans la conversation et la mémoire multi-niveaux
        self.conversation_manager.add_message(sid, MessageRole.USER, query)
        self.conversation_manager.add_message(sid, MessageRole.ASSISTANT, response.content)
        self.memory_manager.add_turn(
            session_id=sid,
            user_message=query,
            assistant_response=response.content,
            org_id=org_id,
            building_id=building_id,
            user_id=user_id,
        )

        return response
