"""Port abstrait vers un fournisseur de prévisions et diagnostics ML."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.sensor_reading import SensorReading


@dataclass(frozen=True)
class ForecastResult:
    """Valeurs prévues et bornes de confiance calculées par un modèle."""

    values: list[float]
    lower: float
    upper: float


@dataclass(frozen=True)
class AnomalyResult:
    """Diagnostic d'anomalie normalisé indépendamment du modèle utilisé."""

    is_anomaly: bool
    score: float
    severity: str


class MLService(ABC):
    """Contrat d'inférence indépendant de XGBoost et scikit-learn."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Retourne la version du modèle actif."""
        raise NotImplementedError

    @abstractmethod
    async def forecast(self, machine_id: str, horizon_hours: int) -> ForecastResult:
        """Prévoit la consommation pour l'horizon demandé."""
        raise NotImplementedError

    @abstractmethod
    async def detect_anomaly(self, readings: list[SensorReading]) -> AnomalyResult:
        """Analyse une séquence de valeurs et retourne un diagnostic."""
        raise NotImplementedError
