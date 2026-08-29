"""
app/ai/conversation.py — Gestion des sessions conversationnelles et historique des échanges.

Maintient l'état des conversations multi-tours, gère le découpage temporel, la limitation
de la fenêtre de contexte et la sérialisation des messages.
"""

from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.ai.types import ChatMessage, MessageRole

logger = logging.getLogger("nouankany.ai")


class ConversationSession(BaseModel):
    """
    Session de conversation unifiée avec métadonnées et historique ordonné.
    """

    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique de la session"
    )
    user_id: Optional[str] = Field(default=None, description="Identifiant de l'utilisateur")
    messages: List[ChatMessage] = Field(
        default_factory=list, description="Historique chronologique des messages"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Date de création UTC"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Dernière mise à jour UTC"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Métadonnées de session (équipement ciblé, etc.)"
    )


class ConversationManager:
    """
    Gestionnaire centralisé en mémoire des sessions conversationnelles.
    """

    def __init__(self, max_messages_per_session: int = 50) -> None:
        """
        Initialise le gestionnaire de conversation.

        :param max_messages_per_session: Nombre maximal de messages conservés par session.
        """
        self.max_messages_per_session = max_messages_per_session
        self._sessions: Dict[str, ConversationSession] = {}
        self._lock = threading.RLock()
        logger.debug("[ConversationManager] Initialisé.")

    def get_or_create_session(
        self, session_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> ConversationSession:
        """
        Récupère une session existante ou en initialise une nouvelle.

        :param session_id: Identifiant de la session (généré si non spécifié).
        :param user_id: Identifiant optionnel de l'utilisateur.
        :return: Instance `ConversationSession`.
        """
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]

            new_id = session_id or str(uuid.uuid4())
            session = ConversationSession(session_id=new_id, user_id=user_id)
            self._sessions[new_id] = session
            logger.debug(f"[ConversationManager] Nouvelle session créée : {new_id}")
            return session

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """
        Ajoute un message à la session spécifiée.

        :param session_id: Identifiant de la session.
        :param role: Rôle de l'émetteur (USER, ASSISTANT, etc.).
        :param content: Texte du message.
        :param metadata: Métadonnées associées.
        :return: Message créé et inséré.
        """
        msg = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        with self._lock:
            session = self.get_or_create_session(session_id)
            session.messages.append(msg)
            session.updated_at = datetime.now(timezone.utc)

            # Élagage si dépassement de la capacité
            if len(session.messages) > self.max_messages_per_session:
                session.messages = session.messages[-self.max_messages_per_session:]

        return msg

    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Retourne l'historique des messages d'une session.

        :param session_id: Identifiant de la session.
        :param limit: Nombre maximum de messages récents à retourner.
        :return: Liste de messages.
        """
        with self._lock:
            if session_id not in self._sessions:
                return []
            msgs = self._sessions[session_id].messages
            if limit and limit > 0:
                return msgs[-limit:]
            return list(msgs)

    def clear_session(self, session_id: str) -> bool:
        """
        Efface les messages d'une session.

        :param session_id: Identifiant de la session à vider.
        :return: True si la session a été vidée, False si introuvable.
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].messages.clear()
                self._sessions[session_id].updated_at = datetime.now(timezone.utc)
                return True
            return False
