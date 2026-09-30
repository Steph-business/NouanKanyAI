"""Adaptateur composite exposant les deux modèles historiques via le port ML."""

from app.application.ports.ml_service import AnomalyResult, ForecastResult, MLService
from app.domain.entities.sensor_reading import SensorReading
from app.infrastructure.ml.isolation_forest_adapter import IsolationForestAdapter
from app.infrastructure.ml.xgboost_adapter import XGBoostAdapter


class CombinedMLAdapter(MLService):
    """Réunit les adaptateurs de prévision et d'anomalie sous un port applicatif unique."""

    def __init__(
        self, forecasting: XGBoostAdapter, anomaly_detection: IsolationForestAdapter
    ) -> None:
        self.forecasting = forecasting
        self.anomaly_detection = anomaly_detection

    @property
    def version(self) -> str:
        """Retourne la version de prévision, commune aux artefacts ML déployés."""
        return self.forecasting.version

    async def forecast(self, machine_id: str, horizon_hours: int) -> ForecastResult:
        """Délègue la prévision à XGBoost."""
        return await self.forecasting.forecast(machine_id, horizon_hours)

    async def detect_anomaly(self, readings: list[SensorReading]) -> AnomalyResult:
        """Délègue la détection à Isolation Forest."""
        return await self.anomaly_detection.detect_anomaly(readings)
