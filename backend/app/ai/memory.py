"""
app/ai/memory.py — Gestionnaires et interfaces de mémoire conversationnelle multi-niveaux.

Fournit une architecture de mémoire découplée et indépendante du fournisseur de LLM :
- Mémoire courte (session active / fenêtre glissante).
- Mémoire longue (persistante par utilisateur, organisation et bâtiment).
- Suivi des préférences, équipements surveillés, recommandations émises et actions confirmées.
- Mécanismes de résumé automatique pour optimiser le contexte sans explosion de tokens.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional
import uuid

from app.ai.types import (
    ChatMessage,
    ConfirmedActionRecord,
    LongTermEntityMemory,
    MessageRole,
    RecommendationRecord,
    UserPreferences,
)

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
        self._lock = threading.RLock()
        logger.debug(f"[ConversationBufferMemory] Initialisé (max_turns={max_turns})")

    def load_memory_variables(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self._lock:
            return {self.memory_key: list(self._messages)}

    def save_context(self, user_input: str, assistant_output: str) -> None:
        with self._lock:
            self._messages.append(ChatMessage(role=MessageRole.USER, content=user_input))
            self._messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=assistant_output))

            # Élagage des tours anciens
            max_messages = self.max_turns * 2
            if len(self._messages) > max_messages:
                self._messages = self._messages[-max_messages:]

    def clear(self) -> None:
        with self._lock:
            self._messages.clear()


class SummaryMemory(BaseMemory):
    """
    Mémoire à résumé synthétique pour la compression de contexte.
    """

    def __init__(self, memory_key: str = "summary") -> None:
        self.memory_key = memory_key
        self.summary_text: str = ""
        self._lock = threading.RLock()
        logger.debug("[SummaryMemory] Initialisé.")

    def load_memory_variables(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self._lock:
            return {self.memory_key: self.summary_text}

    def save_context(self, user_input: str, assistant_output: str) -> None:
        with self._lock:
            if not self.summary_text:
                self.summary_text = f"Discussion sur: {user_input[:80]}..."
            else:
                self.summary_text += f" | Suivi: {user_input[:40]}..."

    def clear(self) -> None:
        with self._lock:
            self.summary_text = ""


class ShortTermSessionMemory:
    """
    Structure de mémoire courte pour une session conversationnelle active.
    """

    def __init__(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        max_messages: int = 14,
    ) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.org_id = org_id
        self.building_id = building_id
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
        self.active_topic: Optional[str] = None
        self.active_machine: Optional[str] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class ConversationMemoryManager:
    """
    Gestionnaire centralisé de mémoire conversationnelle multi-niveaux et multi-tenant.
    Organise la mémoire par utilisateur, organisation et bâtiment, avec compression automatique.
    Totalement indépendant de tout fournisseur de LLM.
    """

    def __init__(self, short_term_max_messages: int = 12) -> None:
        """
        Initialise le gestionnaire de mémoire.

        :param short_term_max_messages: Seuil de messages avant déclenchement du résumé automatique.
        """
        self.short_term_max_messages = short_term_max_messages
        self._short_term_sessions: Dict[str, ShortTermSessionMemory] = {}
        self._long_term_entities: Dict[str, LongTermEntityMemory] = {}
        self._lock = threading.RLock()
        logger.info("[ConversationMemoryManager] Gestionnaire de mémoire initialisé.")

    @staticmethod
    def build_entity_key(
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Génère une clé hiérarchique unique pour le stockage long terme.

        :param org_id: Identifiant de l'organisation.
        :param building_id: Identifiant du bâtiment/site.
        :param user_id: Identifiant de l'utilisateur.
        :return: Clé composite standardisée.
        """
        o = org_id or "default_org"
        b = building_id or "default_building"
        u = user_id or "default_user"
        return f"{o}:{b}:{u}"

    def get_or_create_short_term(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
    ) -> ShortTermSessionMemory:
        """
        Récupère ou initialise la mémoire courte de session.
        """
        with self._lock:
            if session_id in self._short_term_sessions:
                return self._short_term_sessions[session_id]

            session = ShortTermSessionMemory(
                session_id=session_id,
                user_id=user_id,
                org_id=org_id,
                building_id=building_id,
                max_messages=self.short_term_max_messages,
            )
            self._short_term_sessions[session_id] = session
            return session

    def get_or_create_long_term(
        self,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> LongTermEntityMemory:
        """
        Récupère ou initialise la mémoire longue associée au périmètre org/bâtiment/utilisateur.
        """
        key = self.build_entity_key(org_id=org_id, building_id=building_id, user_id=user_id)
        with self._lock:
            if key in self._long_term_entities:
                return self._long_term_entities[key]

            entity = LongTermEntityMemory(
                entity_key=key,
                org_id=org_id,
                building_id=building_id,
                user_id=user_id,
                preferences=UserPreferences(),
            )
            self._long_term_entities[key] = entity
            return entity

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Enregistre un tour de parole dans la mémoire courte et gère la compression automatique.

        :param session_id: Identifiant de session.
        :param user_message: Question de l'utilisateur.
        :param assistant_response: Réponse de l'assistant.
        :param org_id: Organisation.
        :param building_id: Bâtiment.
        :param user_id: Utilisateur.
        :param metadata: Métadonnées associées.
        """
        with self._lock:
            short_mem = self.get_or_create_short_term(
                session_id=session_id, user_id=user_id, org_id=org_id, building_id=building_id
            )
            long_mem = self.get_or_create_long_term(
                org_id=org_id, building_id=building_id, user_id=user_id
            )

            # Ajout des deux messages
            meta = metadata or {}
            msg_u = ChatMessage(role=MessageRole.USER, content=user_message, metadata=meta)
            msg_a = ChatMessage(role=MessageRole.ASSISTANT, content=assistant_response, metadata=meta)
            short_mem.messages.extend([msg_u, msg_a])
            short_mem.updated_at = datetime.now(timezone.utc)

            # Vérification du dépassement de la fenêtre courte -> Résumé automatique
            if len(short_mem.messages) > short_mem.max_messages:
                # Les messages anciens sont condensés
                overflow_count = len(short_mem.messages) - short_mem.max_messages
                messages_to_summarize = short_mem.messages[:overflow_count]
                short_mem.messages = short_mem.messages[overflow_count:]

                summary_text = self.generate_auto_summary(messages_to_summarize)
                if summary_text:
                    long_mem.conversation_summaries.append(summary_text)
                    # Conserver un maximum de 10 résumés historiques
                    if len(long_mem.conversation_summaries) > 10:
                        long_mem.conversation_summaries.pop(0)
                    long_mem.updated_at = datetime.now(timezone.utc)
                    logger.debug(
                        f"[ConversationMemoryManager] Résumé auto archivé pour {long_mem.entity_key} : {summary_text}"
                    )

    def generate_auto_summary(self, messages: List[ChatMessage]) -> str:
        """
        Génère une synthèse concise des échanges archivés sans dépendance externe.

        :param messages: Liste des messages à résumer.
        :return: Synthèse textuelle.
        """
        if not messages:
            return ""

        topics: List[str] = []
        for m in messages:
            if m.role == MessageRole.USER:
                # Extraction des mots-clés clés / débuts de phrases
                clean = m.content.strip().replace("\n", " ")
                if len(clean) > 60:
                    clean = clean[:57] + "..."
                topics.append(clean)

        timestamp_str = datetime.now(timezone.utc).strftime("%d/%m %H:%M")
        return f"[{timestamp_str}] Échanges précédents : " + " ; ".join(topics[:4])

    def update_preferences(
        self,
        preferences: UserPreferences,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Met à jour les préférences de l'entité."""
        with self._lock:
            entity = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            entity.preferences = preferences
            entity.updated_at = datetime.now(timezone.utc)

    def add_tracked_equipment(
        self,
        equipment_names: List[str],
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[str]:
        """Ajoute des équipements à la liste des équipements surveillés."""
        with self._lock:
            entity = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            for eq in equipment_names:
                eq_clean = eq.strip()
                if eq_clean and eq_clean not in entity.tracked_equipments:
                    entity.tracked_equipments.append(eq_clean)
            entity.updated_at = datetime.now(timezone.utc)
            return list(entity.tracked_equipments)

    def remove_tracked_equipment(
        self,
        equipment_name: str,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Retire un équipement de la surveillance."""
        with self._lock:
            entity = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            if equipment_name in entity.tracked_equipments:
                entity.tracked_equipments.remove(equipment_name)
                entity.updated_at = datetime.now(timezone.utc)
                return True
            return False

    def record_recommendation(
        self,
        title: str,
        description: str,
        target_machine: Optional[str] = None,
        estimated_savings_fcfa: float = 0.0,
        estimated_savings_kwh: float = 0.0,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> RecommendationRecord:
        """Consigne une recommandation générée par l'assistant."""
        rec = RecommendationRecord(
            title=title,
            description=description,
            target_machine=target_machine,
            estimated_savings_fcfa=estimated_savings_fcfa,
            estimated_savings_kwh=estimated_savings_kwh,
        )
        with self._lock:
            entity = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            entity.recommendation_history.append(rec)
            # Limiter à 50 recommandations conservées
            if len(entity.recommendation_history) > 50:
                entity.recommendation_history.pop(0)
            entity.updated_at = datetime.now(timezone.utc)
        return rec

    def confirm_action(
        self,
        action_type: str,
        user_id: str,
        machine_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        realized_savings_fcfa: float = 0.0,
        realized_savings_kwh: float = 0.0,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
    ) -> ConfirmedActionRecord:
        """Enregistre une action validée et incrémente les économies cumulées."""
        action = ConfirmedActionRecord(
            action_type=action_type,
            user_id=user_id,
            machine_id=machine_id,
            details=details or {},
            realized_savings_fcfa=realized_savings_fcfa,
            realized_savings_kwh=realized_savings_kwh,
            building_id=building_id,
            org_id=org_id,
        )
        with self._lock:
            entity = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            entity.confirmed_actions.append(action)
            entity.cumulative_savings_fcfa += realized_savings_fcfa
            entity.cumulative_savings_kwh += realized_savings_kwh
            if len(entity.confirmed_actions) > 50:
                entity.confirmed_actions.pop(0)
            entity.updated_at = datetime.now(timezone.utc)
        return action

    def get_relevant_context_for_prompt(
        self,
        session_id: Optional[str] = None,
        org_id: Optional[str] = None,
        building_id: Optional[str] = None,
        user_id: Optional[str] = None,
        query: Optional[str] = None,
    ) -> str:
        """
        Expose une synthèse ciblée et compacte de la mémoire pour l'injection dans PromptBuilder.

        :param session_id: Session active.
        :param org_id: Organisation.
        :param building_id: Bâtiment.
        :param user_id: Utilisateur.
        :param query: Requête courante pour affiner la pertinence.
        :return: Bloc textuel formaté en Markdown.
        """
        with self._lock:
            long_mem = self.get_or_create_long_term(org_id=org_id, building_id=building_id, user_id=user_id)
            sections: List[str] = []

            # 1. Préférences opérationnelles
            pref = long_mem.preferences
            sections.append(
                f"- **Préférences du site** : Seuil d'alerte={pref.energy_alert_threshold_kw} kW | "
                f"Devise={pref.currency} | Grille={pref.preferred_tariff_schedule}"
            )

            # 2. Équipements surveillés
            if long_mem.tracked_equipments:
                eq_str = ", ".join(long_mem.tracked_equipments)
                sections.append(f"- **Équipements prioritaires surveillés** : {eq_str}")

            # 3. Actions récentes confirmées & Économies cumulées
            if long_mem.confirmed_actions:
                last_actions = long_mem.confirmed_actions[-3:]
                act_summaries = [
                    f"{a.action_type} sur {a.machine_id or 'site'} ({a.realized_savings_fcfa:.0f} FCFA économisés)"
                    for a in last_actions
                ]
                sections.append(f"- **Dernières actions validées** : {'; '.join(act_summaries)}")

            if long_mem.cumulative_savings_fcfa > 0:
                sections.append(
                    f"- **Total des économies cumulées validées** : {long_mem.cumulative_savings_fcfa:,.0f} FCFA "
                    f"({long_mem.cumulative_savings_kwh:,.1f} kWh)"
                )

            # 4. Résumés des sessions passées si existants
            if long_mem.conversation_summaries:
                last_summaries = long_mem.conversation_summaries[-2:]
                sections.append(f"- **Historique condensé des échanges** : {' | '.join(last_summaries)}")

            if not sections:
                return ""

            return "### [MÉMOIRE & HISTORIQUE DU SITE]\n" + "\n".join(sections)
