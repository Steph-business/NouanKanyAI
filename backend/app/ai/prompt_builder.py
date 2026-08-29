"""
app/ai/prompt_builder.py — Constructeur de prompts et gestion des instructions système pour NouanKanyAI.

Gère les gabarits d'instructions système orientés efficacité énergétique industrielle,
l'intégration des politiques tarifaires CIE, le formatage des exemples et l'assemblage de prompts modulaires.
"""

from typing import Any, Dict, List, Optional
from app.ai.types import ChatMessage, MessageRole


DEFAULT_SYSTEM_INSTRUCTION = """Tu es NouanKanyAI Copilot, l'assistant d'intelligence artificielle expert en gestion et optimisation énergétique industrielle pour l'Afrique de l'Ouest (en particulier la Côte d'Ivoire).

Tes responsabilités principales :
1. Analyser la consommation électrique en temps réel et prévisionnelle (kW, kWh).
2. Expliquer les anomalies opérationnelles et dérives d'équipements industriels (presses, compresseurs, fours, convoyeurs).
3. Recommander des actions d'effacement et de délestage pour éviter les dépassements de puissance souscrite lors des heures de pointe (19h-23h CIE).
4. Calculer et optimiser l'impact financier en Francs CFA (FCFA) selon la grille tarifaire officielle de la CIE (Heures Pleines, Heures Creuses, Heures de Pointe).
5. Fournir des explications claires, précises, professionnelles et directement actionnables par les ingénieurs d'exploitation et directeurs d'usine.

Règles de communication :
- Sois rigoureux, concis et factuel.
- Exprime les coûts en FCFA et les puissances en kW.
- Si des données d'équipements ou d'alertes sont fournies dans le contexte, utilise-les en priorité.
- Si une information requise manque, pose une question de clarification ciblée.
"""


class PromptBuilder:
    """
    Constructeur et assembleur dynamique de prompts pour les modèles de langage.
    """

    def __init__(
        self,
        system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
        role_description: Optional[str] = None,
    ) -> None:
        """
        Initialise le constructeur de prompt.

        :param system_instruction: Directive système de base.
        :param role_description: Spécification complémentaire de posture ou persona.
        """
        self.system_instruction = system_instruction
        self.role_description = role_description

    def build_system_instruction(
        self,
        additional_guidelines: Optional[List[str]] = None,
        custom_context: Optional[str] = None,
    ) -> str:
        """
        Assemble l'instruction système finale avec directives optionnelles.

        :param additional_guidelines: Règles métiers supplémentaires.
        :param custom_context: Contexte statique additionnel.
        :return: Instruction système complète prête pour le LLM.
        """
        instruction = self.system_instruction

        if self.role_description:
            instruction += f"\n\nRôle spécifique : {self.role_description}"

        if custom_context:
            instruction += f"\n\nContexte d'entreprise :\n{custom_context}"

        if additional_guidelines:
            instruction += "\n\nDirectives impératives :\n"
            for g in additional_guidelines:
                instruction += f"- {g}\n"

        return instruction.strip()

    def format_user_prompt(
        self,
        query: str,
        industrial_context: Optional[str] = None,
        rag_context: Optional[str] = None,
    ) -> str:
        """
        Structure le message utilisateur en y adjoignant les contextes temps réel et RAG.

        :param query: Question ou requête brute de l'utilisateur.
        :param industrial_context: Données télémétriques et état des machines au format texte/markdown.
        :param rag_context: Extraits documentaires pertinents issus du moteur RAG.
        :return: Prompt utilisateur enrichi.
        """
        sections: List[str] = []

        if industrial_context:
            sections.append(f"### [CONTEXTE INDUSTRIEL TEMPS RÉEL]\n{industrial_context}")

        if rag_context:
            sections.append(f"### [DOCUMENTATION TECHNIQUE & PROCÉDURES]\n{rag_context}")

        sections.append(f"### [REQUÊTE DE L'UTILISATEUR]\n{query}")

        return "\n\n".join(sections)

    def create_chat_messages(
        self,
        query: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        industrial_context: Optional[str] = None,
        rag_context: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Assemble la liste ordonnée des messages pour une requête de chat multi-tours.

        :param query: Requête courante de l'utilisateur.
        :param conversation_history: Historique des échanges précédents.
        :param industrial_context: Contexte machine / alertes.
        :param rag_context: Contexte documentaire.
        :return: Liste complète des `ChatMessage`.
        """
        messages: List[ChatMessage] = []

        if conversation_history:
            messages.extend(conversation_history)

        formatted_content = self.format_user_prompt(
            query=query,
            industrial_context=industrial_context,
            rag_context=rag_context,
        )

        messages.append(
            ChatMessage(role=MessageRole.USER, content=formatted_content)
        )

        return messages
