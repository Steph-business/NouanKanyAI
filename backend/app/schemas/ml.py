"""
schemas/ml.py — Schémas Pydantic v2 pour l'interaction avec la couche ML.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ForecasterInputSchema(BaseModel):
    """
    Schéma de validation des caractéristiques d'entrée pour le modèle de prévision (XGBoost).
    """

    model_config = ConfigDict(extra="ignore")

    power_kw: float = Field(..., description="Consommation actuelle en kW", ge=0.0)
    power_kw_lag_1: float = Field(..., description="Consommation t-1h en kW", ge=0.0)
    power_kw_lag_6: float = Field(..., description="Consommation t-6h en kW", ge=0.0)
    power_kw_lag_24: float = Field(..., description="Consommation t-24h en kW", ge=0.0)
    power_rolling_mean: float = Field(
        ..., description="Moyenne mobile de consommation", ge=0.0
    )
    power_rolling_std: float = Field(
        ..., description="Écart-type mobile de consommation", ge=0.0
    )
    hour: int = Field(..., description="Heure de la journée (0-23)", ge=0, le=23)
    day_of_week: int = Field(
        ..., description="Jour de la semaine (0=Lundi, 6=Dimanche)", ge=0, le=6
    )
    is_weekend: int = Field(..., description="Indicateur de week-end (0 ou 1)", ge=0, le=1)
    is_peak_hour: int = Field(
        ..., description="Indicateur d'heure de pointe (0 ou 1)", ge=0, le=1
    )
    temperature_c: float = Field(
        ..., description="Température ambiante en degrés Celsius"
    )


class AnomalyInputSchema(BaseModel):
    """
    Schéma de validation des caractéristiques d'entrée pour la détection d'anomalies (Isolation Forest).
    """

    model_config = ConfigDict(extra="ignore")

    power_kw: float = Field(..., description="Consommation actuelle en kW", ge=0.0)
    temperature_c: float = Field(
        ..., description="Température ambiante en degrés Celsius"
    )
    vibration_hz: float = Field(..., description="Fréquence de vibration en Hz", ge=0.0)
    pressure_bar: float = Field(..., description="Pression enregistrée en bars", ge=0.0)
    power_rolling_std: float = Field(
        ..., description="Écart-type mobile de consommation", ge=0.0
    )
    consumption_delta: float = Field(
        ..., description="Variation de consommation par rapport au pas précédent"
    )
    hour: int = Field(..., description="Heure de la journée (0-23)", ge=0, le=23)


class GenericFeaturesInput(BaseModel):
    """
    Schéma d'entrée générique acceptant un dictionnaire de caractéristiques.
    """

    model_config = ConfigDict(extra="ignore")

    features: Dict[str, Any] = Field(
        ..., description="Dictionnaire clé-valeur des caractéristiques fournies"
    )


class PredictionResponseSchema(BaseModel):
    """
    Schéma de réponse pour une prédiction énergétique.
    """

    prediction: float = Field(..., description="Valeur prédite pour t+1h")
    unit: str = Field(default="kW", description="Unité de mesure")
    model_name: str = Field(..., description="Nom du modèle ayant généré la prédiction")
    model_version: str = Field(..., description="Version du modèle utilisé")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Métadonnées complémentaires"
    )


class AnomalyResponseSchema(BaseModel):
    """
    Schéma de réponse pour une analyse d'anomalie.
    """

    is_anomaly: bool = Field(..., description="Indique si une anomalie a été détectée")
    anomaly_score: float = Field(
        ..., description="Score brut de décision d'Isolation Forest"
    )
    anomaly_probability: float = Field(
        ..., description="Probabilité estimée d'anomalie (0.0 à 1.0)"
    )
    confidence: float = Field(
        ..., description="Niveau de confiance dans le résultat (0.0 à 1.0)"
    )
    model_name: str = Field(..., description="Nom du modèle utilisé")
    model_version: str = Field(..., description="Version du modèle utilisé")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Métadonnées d'exécution"
    )
