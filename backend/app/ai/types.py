"""
app/ai/types.py — Structures de données typées et contrats d'échange pour la couche GenAI.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """
    Rôle de l'émetteur d'un message dans une conversation IA.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """
    Représente un message individuel dans le fil de discussion.
    """

    model_config = ConfigDict(frozen=True)

    role: MessageRole = Field(..., description="Rôle de l'émetteur du message")
    content: str = Field(..., description="Contenu textuel du message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Horodatage UTC du message",
    )
    name: Optional[str] = Field(default=None, description="Nom de l'auteur ou de l'outil")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Appels d'outils éventuels demandés par le modèle"
    )
    tool_call_id: Optional[str] = Field(
        default=None, description="Identifiant de l'appel d'outil associé en cas de retour d'outil"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Métadonnées arbitraires associées au message"
    )


class GenerationConfig(BaseModel):
    """
    Paramètres de génération et d'échantillonnage pour le LLM.
    """

    model_config = ConfigDict(frozen=True)

    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Créativité de la réponse")
    top_p: float = Field(default=0.95, ge=0.0, le=1.0, description="Seuil de noyau de probabilité")
    top_k: int = Field(default=40, ge=1, description="Nombre de tokens candidats considérés")
    max_output_tokens: int = Field(default=2048, ge=1, description="Longueur maximale de réponse")
    stop_sequences: Optional[List[str]] = Field(
        default=None, description="Séquences d'arrêt de génération"
    )


class AIResponse(BaseModel):
    """
    Réponse structurée retournée par l'AI Gateway après traitement par le LLM.
    """

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="Texte généré par le modèle")
    model_name: str = Field(..., description="Identifiant du modèle ayant répondu")
    latency_ms: float = Field(..., description="Temps total de traitement en millisecondes")
    finish_reason: Optional[str] = Field(default="STOP", description="Raison d'arrêt de la génération")
    usage_tokens: Dict[str, int] = Field(
        default_factory=dict, description="Comptage des tokens (prompt, completion, total)"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Appels d'outils identifiés"
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID unique de traçabilité de la requête",
    )
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None, description="Réponse brute du fournisseur d'API"
    )


class ToolDefinition(BaseModel):
    """
    Définition d'un outil métier appelable par l'IA (Function Calling).
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Nom technique unique de la fonction")
    description: str = Field(..., description="Description détaillée de l'utilité de la fonction")
    parameters_schema: Dict[str, Any] = Field(
        default_factory=dict, description="Schéma JSON des paramètres attendus"
    )


class ToolResult(BaseModel):
    """
    Résultat normalisé retourné par l'exécution d'un outil métier.
    """

    model_config = ConfigDict(frozen=True)

    tool_name: str = Field(..., description="Nom de l'outil exécuté")
    success: bool = Field(default=True, description="Indique si l'exécution a réussi sans erreur")
    data: Dict[str, Any] = Field(default_factory=dict, description="Données de sortie normalisées")
    error: Optional[str] = Field(default=None, description="Message d'erreur en cas d'échec")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Horodatage UTC de l'exécution"
    )
    execution_time_ms: float = Field(default=0.0, description="Durée de l'exécution en millisecondes")


class DocumentChunk(BaseModel):
    """
    Segment textuel documentaire pour l'indexation et la recherche vectorielle (RAG).
    """

    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique du chunk"
    )
    document_id: str = Field(..., description="Identifiant du document source")
    content: str = Field(..., description="Contenu textuel du segment")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Métadonnées (source, section, page, date)"
    )
    score: Optional[float] = Field(default=None, description="Score de pertinence vectorielle")


class RetrievalResult(BaseModel):
    """
    Résultat d'une recherche documentaire vectorielle.
    """

    model_config = ConfigDict(frozen=True)

    query: str = Field(..., description="Requête de recherche d'origine")
    chunks: List[DocumentChunk] = Field(
        default_factory=list, description="Segments documentaires pertinents ordonnés"
    )
    latency_ms: float = Field(default=0.0, description="Durée de la recherche en ms")
    total_found: int = Field(default=0, description="Nombre de documents correspondants")


# =====================================================================
# Modèles de Mémoire Conversationnelle (Court et Long Terme)
# =====================================================================

class UserPreferences(BaseModel):
    """
    Préférences opérationnelles et de tarification de l'utilisateur ou du site.
    """

    language: str = Field(default="fr", description="Langue de réponse préférée")
    currency: str = Field(default="FCFA", description="Devise monétaire pour les bilans financiers")
    energy_alert_threshold_kw: float = Field(
        default=100.0, ge=0.0, description="Seuil d'alerte de surconsommation en kW"
    )
    preferred_tariff_schedule: str = Field(
        default="CIE_STANDARD", description="Grille tarifaire (CIE_STANDARD, CIE_INDUSTRIEL, etc.)"
    )
    auto_delestage_allowed: bool = Field(
        default=False, description="Autorisation d'assistance au délestage automatique"
    )
    custom_parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Paramètres personnalisés supplémentaires"
    )


class RecommendationRecord(BaseModel):
    """
    Historique d'une recommandation d'effacement ou d'optimisation émise par l'assistant.
    """

    recommendation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique de la recommandation"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Horodatage UTC d'émission"
    )
    title: str = Field(..., description="Titre concis de la recommandation")
    description: str = Field(..., description="Détail de l'action préconisée")
    target_machine: Optional[str] = Field(default=None, description="Équipement ciblé")
    estimated_savings_kwh: float = Field(default=0.0, ge=0.0, description="Gain énergétique estimé (kWh)")
    estimated_savings_fcfa: float = Field(default=0.0, ge=0.0, description="Gain financier estimé (FCFA)")
    status: str = Field(
        default="proposed", description="Statut (proposed, confirmed, rejected, executed)"
    )
    confirmed_at: Optional[datetime] = Field(default=None, description="Date de confirmation")


class ConfirmedActionRecord(BaseModel):
    """
    Action opérationnelle confirmée ou exécutée par l'opérateur / directeur.
    """

    action_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Identifiant unique de l'action"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Horodatage UTC de l'action"
    )
    action_type: str = Field(
        ..., description="Type d'action (shed_load, eco_mode, maintenance_rescheduled, set_threshold)"
    )
    machine_id: Optional[str] = Field(default=None, description="Identifiant ou nom de la machine")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Détails contextuels de l'action"
    )
    user_id: str = Field(..., description="Utilisateur ayant validé l'action")
    building_id: Optional[str] = Field(default=None, description="Bâtiment concerné")
    org_id: Optional[str] = Field(default=None, description="Organisation concernée")
    realized_savings_fcfa: float = Field(
        default=0.0, ge=0.0, description="Économies réelles calculées (FCFA)"
    )
    realized_savings_kwh: float = Field(
        default=0.0, ge=0.0, description="Énergie économisée (kWh)"
    )


class LongTermEntityMemory(BaseModel):
    """
    Mémoire persistante structurée associée à un utilisateur, bâtiment ou organisation.
    """

    entity_key: str = Field(..., description="Clé composite d'identification (org:bldg:user)")
    org_id: Optional[str] = Field(default=None, description="Identifiant de l'organisation")
    building_id: Optional[str] = Field(default=None, description="Identifiant du bâtiment/site")
    user_id: Optional[str] = Field(default=None, description="Identifiant de l'utilisateur")
    tracked_equipments: List[str] = Field(
        default_factory=list, description="Liste des équipements spécifiquement surveillés"
    )
    preferences: UserPreferences = Field(
        default_factory=UserPreferences, description="Préférences opérationnelles"
    )
    recommendation_history: List[RecommendationRecord] = Field(
        default_factory=list, description="Historique des recommandations émises"
    )
    confirmed_actions: List[ConfirmedActionRecord] = Field(
        default_factory=list, description="Historique des actions confirmées"
    )
    conversation_summaries: List[str] = Field(
        default_factory=list, description="Synthèses des sessions antérieures"
    )
    cumulative_savings_fcfa: float = Field(
        default=0.0, ge=0.0, description="Cumul historique des économies (FCFA)"
    )
    cumulative_savings_kwh: float = Field(
        default=0.0, ge=0.0, description="Cumul historique d'énergie économisée (kWh)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Dernière mise à jour UTC"
    )
