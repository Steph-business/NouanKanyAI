"""
app/ai/memory.py — Gestionnaires et interfaces de mémoire conversationnelle (Memory).

Définit les contrats d'abstraction pour maintenir le contexte à long et court terme
des échanges avec les opérateurs industriels (historique immédiat, résumés périodiques).
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional
from app.ai.types import ChatMessage, MessageRole

logger = logging.getLogger("nouankany.ai")


class BaseMemory(ABC):
    """
    Interface abstraite pour les systèmes de gestion de mémoire conversationnelle.
    """

    @abstractmethod
    def load_memory_variables(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Charge et formate les variables de mémoire à injecter dans le prompt.

        :param inputs: Données d'entrée contextuelles optionnelles.
        :return: Dictionnaire contenant les éléments de mémoire (ex: 'history', 'summary').
        """
        pass

    @abstractmethod
    def save_context(self, user_input: str, assistant_output: str) -> None:
        """
        Enregistre un tour de parole dans la mémoire.

        :param user_input: Message de l'utilisateur.
        :param assistant_output: Réponse produite par l'assistant.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Réinitialise intégralement la mémoire."""
        pass


class ConversationBufferMemory(BaseMemory):
    """
    Mémoire tampon conservant les N derniers tours de parole en mémoire vive.
    """

    def __init__(self, max_turns: int = 10, memory_key: str = "history") -> None:
        self.max_turns = max_turns
        self.memory_key = memory_key
        self._messages: List[ChatMessage] = []
        logger.debug(f"[ConversationBufferMemory] Initialisé (max_turns={max_turns})")

    def load_memory_variables(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {self.memory_key: list(self._messages)}

    def save_context(self, user_input: str, assistant_output: str) -> None:
        self._messages.append(ChatMessage(role=MessageRole.USER, content=user_input))
        self._messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=assistant_output))

        # Élagage des tours anciens
        max_messages = self.max_turns * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]

    def clear(self) -> None:
        self._messages.clear()


class SummaryMemory(BaseMemory):
    """
    Point d'extension pour la mémoire à résumé synthétique (compressée par LLM).
    """

    def __init__(self, memory_key: str = "summary") -> None:
        self.memory_key = memory_key
        self.summary_text: str = ""
        logger.debug("[SummaryMemory] Initialisé.")

    def load_memory_variables(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {self.memory_key: self.summary_text}

    def save_context(self, user_input: str, assistant_output: str) -> None:
        # Point d'extension : génération de résumé incrémental dans les étapes futures
        if not self.summary_text:
            self.summary_text = f"Discussion sur: {user_input[:80]}..."
        else:
            self.summary_text += f" | Suivi: {user_input[:40]}..."

    def clear(self) -> None:
        self.summary_text = ""
