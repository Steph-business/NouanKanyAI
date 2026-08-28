"""
schemas/ml.py — Schémas Pydantic v2 pour l'API REST de Machine Learning NouanKanyAI.

Définit les contrats de données d'entrée, de sortie, d'erreur et de monitoring
avec documentation OpenAPI exhaustive et exemples réalistes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# =====================================================================
# Schémas de Requête (Inputs)
# =====================================================================

class ForecastingRequest(BaseModel):
    """
    Données d'entrée pour la prévision de consommation énergétique (t+1h).
    Accepte soit les caractéristiques brutes (les lags et métriques temporelles
    seront alors calculés automatiquement), soit les caractéristiques complètes précalculées.
    """

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "power_kw": 85.5,
                "temperature_c": 32.0,
                "hour": 14,
                "day_of_week": 2,
                "is_weekend": 0,
                "is_peak_hour": 1,
                "power_kw_lag_1": 80.0,
                "power_kw_lag_6": 75.0,
                "power_kw_lag_24": 70.0,
                "power_rolling_mean": 78.5,
                "power_rolling_std": 3.2,
            }
        },
    )

    power_kw: float = Field(
        ..., description="Puissance active actuelle en kW", ge=0.0
    )
    temperature_c: Optional[float] = Field(
        default=28.0, description="Température ambiante (°C)"
    )
    hour: Optional[int] = Field(
        default=None, description="Heure (0-23). Si omise, déduite de l'horodatage UTC.", ge=0, le=23
    )
    day_of_week: Optional[int] = Field(
        default=None, description="Jour de semaine (0=Lundi, 6=Dimanche). Déduit si omis.", ge=0, le=6
    )
    is_weekend: Optional[int] = Field(
        default=None, description="1 si week-end, 0 sinon. Déduit si omis.", ge=0, le=1
    )
    is_peak_hour: Optional[int] = Field(
        default=None, description="1 si heure de pointe, 0 sinon. Déduit si omis.", ge=0, le=1
    )
    power_kw_lag_1: Optional[float] = Field(
        default=None, description="Puissance à t-1h (kW). Déduite si omise."
    )
    power_kw_lag_6: Optional[float] = Field(
        default=None, description="Puissance à t-6h (kW). Déduite si omise."
    )
    power_kw_lag_24: Optional[float] = Field(
        default=None, description="Puissance à t-24h (kW). Déduite si omise."
    )
    power_rolling_mean: Optional[float] = Field(
        default=None, description="Moyenne mobile de puissance (kW). Déduite si omise."
    )
    power_rolling_std: Optional[float] = Field(
        default=None, description="Écart-type mobile de puissance (kW). Déduit si omis."
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Historique optionnel de lectures pour calcul précis des retards"
    )
    strict_bounds: Optional[bool] = Field(
        default=False, description="Si True, rejette strictement les données hors bornes du schéma"
    )


class AnomalyDetectionRequest(BaseModel):
    """
    Données d'observation capteurs pour la détection d'anomalies (Isolation Forest).
    """

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "power_kw": 185.0,
                "temperature_c": 75.0,
                "vibration_hz": 42.5,
                "pressure_bar": 3.8,
                "hour": 15,
                "power_rolling_std": 12.0,
                "consumption_delta": 45.0,
            }
        },
    )

    power_kw: float = Field(
        ..., description="Puissance active mesurée en kW", ge=0.0
    )
    temperature_c: float = Field(
        ..., description="Température mesurée sur l'équipement en °C"
    )
    vibration_hz: float = Field(
        ..., description="Fréquence de vibration en Hz", ge=0.0
    )
    pressure_bar: float = Field(
        ..., description="Pression enregistrée en bars", ge=0.0
    )
    power_rolling_std: Optional[float] = Field(
        default=0.0, description="Écart-type mobile de consommation"
    )
    consumption_delta: Optional[float] = Field(
        default=0.0, description="Variation de consommation par rapport au pas précédent"
    )
    hour: Optional[int] = Field(
        default=None, description="Heure de l'observation (0-23). Déduite si omise.", ge=0, le=23
    )
    previous_power: Optional[float] = Field(
        default=None, description="Puissance de l'itération précédente pour calculer consumption_delta"
    )
    strict_bounds: Optional[bool] = Field(
        default=False, description="Si True, applique une vérification stricte des plages de valeurs"
    )


# =====================================================================
# Schémas de Réponse (Outputs)
# =====================================================================

class PredictionMetadataSchema(BaseModel):
    """
    Métadonnées d'exécution d'une inférence.
    """

    model_config = ConfigDict(frozen=True)

    request_id: str = Field(..., description="UUID unique de la requête")
    execution_time_ms: float = Field(..., description="Durée de traitement en millisecondes")
    timestamp: datetime = Field(..., description="Horodatage UTC de la prédiction")
    feature_count: int = Field(..., description="Nombre de variables utilisées")
    data_hash: Optional[str] = Field(default=None, description="Empreinte SHA-256 des données d'entrée")


class PredictionResponseSchema(BaseModel):
    """
    Réponse structurée d'une prévision énergétique à t+1 heure.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "request_id": "a6036359-8a65-4c41-969f-5dbc2112c7af",
                "prediction": 88.42,
                "unit": "kW",
                "model_name": "XGBoost_Forecaster",
                "model_version": "2.0.0",
                "metadata": {
                    "request_id": "a6036359-8a65-4c41-969f-5dbc2112c7af",
                    "execution_time_ms": 15.42,
                    "timestamp": "2026-08-28T14:30:00Z",
                    "feature_count": 11,
                    "data_hash": "a0e5adb0324ae5cf2a891d97e7223e88f63a61baa05b90ddf2da2a9c69d03696",
                },
            }
        },
    )

    request_id: str = Field(..., description="Identifiant unique universel (UUID) de la requête")
    prediction: float = Field(..., description="Puissance électrique prédite pour t+1h en kW")
    unit: str = Field(default="kW", description="Unité physique de la prédiction")
    model_name: str = Field(..., description="Nom du modèle ayant exécuté la prévision")
    model_version: str = Field(..., description="Version du modèle appliqué")
    metadata: PredictionMetadataSchema = Field(..., description="Métadonnées d'inférence associées")


class AnomalyResponseSchema(BaseModel):
    """
    Réponse structurée d'une analyse de détection d'anomalie.
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "request_id": "454a1a7c-cf29-401d-852d-283bbbff98bf",
                "is_anomaly": True,
                "anomaly_score": -0.1542,
                "anomaly_probability": 0.6845,
                "confidence": 0.6542,
                "severity": "modérée",
                "model_name": "IsolationForest_AnomalyDetector",
                "model_version": "2.0.0",
                "metadata": {
                    "request_id": "454a1a7c-cf29-401d-852d-283bbbff98bf",
                    "execution_time_ms": 18.25,
                    "timestamp": "2026-08-28T14:30:00Z",
                    "feature_count": 7,
                    "data_hash": "28849da41738771bd8037848250a676651b395ad0c0fe8381d65db9bb7641351",
                },
            }
        },
    )

    request_id: str = Field(..., description="Identifiant unique universel (UUID) de la requête")
    is_anomaly: bool = Field(..., description="Vrai si l'observation est jugée anormale")
    anomaly_score: float = Field(..., description="Score brut de décision (score négatif = anomalie)")
    anomaly_probability: float = Field(..., description="Probabilité calibrée d'anomalie (0.0 à 1.0)")
    confidence: float = Field(..., description="Score de confiance du diagnostic (0.0 à 1.0)")
    severity: str = Field(
        default="normal",
        description="Niveau de gravité (normal, faible, modérée, critique)",
    )
    model_name: str = Field(..., description="Nom du modèle utilisé")
    model_version: str = Field(..., description="Version du modèle utilisé")
    metadata: PredictionMetadataSchema = Field(..., description="Métadonnées d'inférence associées")


class ReloadResponseSchema(BaseModel):
    """
    Réponse à une demande de rechargement à chaud des modèles.
    """

    status: str = Field(default="reloaded", description="Statut de l'opération de rechargement")
    message: str = Field(..., description="Message de confirmation")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Horodatage du rechargement",
    )
    version: str = Field(..., description="Version rechargée des modèles")
    active_models: List[str] = Field(..., description="Liste des modèles opérationnels")


class ErrorDetail(BaseModel):
    """
    Détail d'une erreur d'API standardisée.
    """

    code: str = Field(..., description="Code d'erreur machine-readable")
    message: str = Field(..., description="Description humaine de l'erreur")
    details: Dict[str, Any] = Field(default_factory=dict, description="Informations de débogage")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Horodatage de l'erreur"
    )
    request_id: Optional[str] = Field(default=None, description="UUID corrélé de la requête")


class StandardErrorResponse(BaseModel):
    """
    Enveloppe standardisée pour toutes les réponses d'erreur de l'API.
    """

    success: bool = Field(default=False, description="Indique un échec de traitement")
    error: ErrorDetail = Field(..., description="Détails de l'erreur")
