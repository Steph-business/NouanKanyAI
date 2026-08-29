"""
app/ai/prompt_models.py — Modèles typés Pydantic v2 pour le constructeur dynamique de prompts.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from app.ai.types import ChatMessage, DocumentChunk, LongTermEntityMemory, UserPreferences


class UserRole(str, Enum):
    """
    Rôles et personas d'utilisateurs supportés par NouanKanyAI.
    """

    ENERGY_MANAGER = "energy_manager"
    PLANT_DIRECTOR = "plant_director"
    OPERATOR = "operator"
    MAINTENANCE_TECH = "maintenance_tech"
    FACILITY_MANAGER = "facility_manager"
    HOTEL_MANAGER = "hotel_manager"
    RESTAURANT_OWNER = "restaurant_owner"
    HOUSEHOLD_HEAD = "household_head"


class BuildingType(str, Enum):
    """
    Typologies de bâtiments et infrastructures prises en charge.
    """

    INDUSTRY = "industry"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    TERTIAIRE = "tertiaire"
    GRAND_MENAGE = "grand_menage"


class MLContext(BaseModel):
    """
    Résultats d'inférence issus du sous-système ML (XGBoost et Isolation Forest).
    """

    model_config = ConfigDict(frozen=True)

    predicted_power_kw: Optional[float] = Field(
        default=None, description="Puissance électrique prédite à t+1h en kW (XGBoost)"
    )
    forecasting_unit: str = Field(default="kW", description="Unité physique de prévision")
    is_anomaly: Optional[bool] = Field(
        default=None, description="Vrai si une anomalie est détectée par Isolation Forest"
    )
    anomaly_score: Optional[float] = Field(
        default=None, description="Score de décision brut d'anomalie"
    )
    anomaly_probability: Optional[float] = Field(
        default=None, description="Probabilité calibrée d'anomalie (0.0 à 1.0)"
    )
    anomaly_severity: Optional[str] = Field(
        default="normal", description="Sévérité (normal, faible, modérée, critique)"
    )
    model_version: Optional[str] = Field(
        default=None, description="Version du modèle ayant produit l'inférence"
    )


class PromptContext(BaseModel):
    """
    Contexte intégral d'assemblage d'un prompt pour le LLM.
    """

    model_config = ConfigDict(extra="allow")

    query: str = Field(..., description="Requête ou question de l'utilisateur")
    role: Union[UserRole, str] = Field(
        default=UserRole.ENERGY_MANAGER, description="Rôle ou persona de l'interlocuteur"
    )
    building_type: Union[BuildingType, str] = Field(
        default=BuildingType.INDUSTRY, description="Type d'infrastructure ou de bâtiment"
    )
    language: str = Field(default="fr", description="Langue cible du prompt et de la réponse")
    currency: str = Field(default="FCFA", description="Devise financière")
    energy_context: Optional[Union[Dict[str, Any], str]] = Field(
        default=None, description="Télémétrie énergétique ou texte de contexte temps réel"
    )
    machines: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Données d'état des équipements"
    )
    alerts: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Alertes opérationnelles actives"
    )
    ml_context: Optional[Union[MLContext, Dict[str, Any]]] = Field(
        default=None, description="Résultats de prévision ou d'anomalie ML"
    )
    rag_context: Optional[Union[List[DocumentChunk], str]] = Field(
        default=None, description="Extraits documentaires ou procédures RAG"
    )
    memory_context: Optional[Union[LongTermEntityMemory, str]] = Field(
        default=None, description="Synthèse de mémoire longue ou préférences"
    )
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, description="Historique des messages précédents"
    )
    additional_instructions: Optional[List[str]] = Field(
        default=None, description="Directives système spécifiques additionnelles"
    )
