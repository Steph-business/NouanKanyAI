"""
app/ml/types.py — Structures de données typées pour la couche ML de NouanKanyAI.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionMetadata(BaseModel):
    """
    Métadonnées associées à une inférence ou prédiction.
    """

    model_config = ConfigDict(frozen=True)

    execution_time_ms: float = Field(
        ..., description="Temps d'exécution de la prédiction en millisecondes"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Horodatage UTC de la réalisation de la prédiction",
    )
    feature_count: int = Field(
        ..., description="Nombre de caractéristiques utilisées pour l'inférence"
    )
    data_hash: Optional[str] = Field(
        default=None, description="Empreinte SHA256 des données transmises"
    )


class PredictionResult(BaseModel):
    """
    Résultat métier d'une prédiction de prévision énergétique.
    """

    model_config = ConfigDict(frozen=True)

    predicted_value: float = Field(
        ..., description="Valeur numérique prédite (ex: puissance en kW)"
    )
    unit: str = Field(default="kW", description="Unité de mesure de la prédiction")
    model_name: str = Field(..., description="Nom exact du modèle appliqué")
    model_version: str = Field(..., description="Version du modèle appliqué")
    metadata: PredictionMetadata = Field(
        ..., description="Métadonnées d'inférence associées"
    )


class AnomalyResult(BaseModel):
    """
    Résultat métier d'une analyse de détection d'anomalie.
    """

    model_config = ConfigDict(frozen=True)

    is_anomaly: bool = Field(
        ..., description="Vrai si l'observation est considérée comme anormale"
    )
    score: float = Field(
        ..., description="Score brut de décision (Isolation Forest decision_function)"
    )
    probability: float = Field(
        ..., description="Probabilité estimée d'anomalie entre 0.0 et 1.0"
    )
    confidence: float = Field(
        ..., description="Score de confiance de l'évaluation entre 0.0 et 1.0"
    )
    model_name: str = Field(..., description="Nom du modèle ayant traité la requête")
    model_version: str = Field(..., description="Version du modèle ayant traité la requête")
    metadata: PredictionMetadata = Field(
        ..., description="Métadonnées d'inférence associées"
    )


class ModelInfo(BaseModel):
    """
    Informations descriptives et métriques d'un modèle enregistré.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Nom du modèle")
    version: str = Field(..., description="Version du modèle")
    model_type: str = Field(
        ..., description="Type de modèle (ex: XGBoost, IsolationForest)"
    )
    status: str = Field(
        ..., description="Statut de promotion (PROMOTED, PASS, FAIL, RESEARCH, etc.)"
    )
    trained_at: Optional[str] = Field(
        default=None, description="Date d'entraînement ou d'export"
    )
    features: List[str] = Field(
        default_factory=list, description="Liste des caractéristiques requises"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Métriques d'évaluation du modèle"
    )
    artifact_path: Optional[str] = Field(
        default=None, description="Chemin relatif ou absolu du fichier d'artefact joblib"
    )


class RegistryEntry(BaseModel):
    """
    Entrée représentant un enregistrement de modèle dans le registre d'expériences.
    """

    model_config = ConfigDict(frozen=True)

    execution_id: str = Field(..., description="Identifiant unique d'exécution/expérience")
    timestamp: str = Field(..., description="Horodatage ISO de l'enregistrement")
    version: str = Field(..., description="Version globale des artefacts créés")
    data_hash: str = Field(..., description="Signature de traçabilité des données")
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Dictionnaire des métriques enregistrées"
    )
    quality_gate: str = Field(
        ..., description="Décision du Quality Gate (ex: PASSED, BLOCKED_BY_QUALITY)"
    )
    changes: List[str] = Field(
        default_factory=list, description="Journal des modifications de la version"
    )


class HealthStatus(BaseModel):
    """
    État de santé global de la couche ML.
    """

    model_config = ConfigDict(frozen=True)

    status: str = Field(
        ..., description="Statut synthétique de la couche ML (ex: healthy, degraded, unhealthy)"
    )
    models_loaded: bool = Field(
        ..., description="Indique si l'ensemble des modèles est chargé en mémoire"
    )
    registry_loaded: bool = Field(
        ..., description="Indique si le registre de déploiement a été chargé"
    )
    feature_schema_loaded: bool = Field(
        ..., description="Indique si le schéma des caractéristiques est accessible"
    )
    version: str = Field(..., description="Version courante active du système ML")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Informations de diagnostic additionnelles"
    )
