"""Adaptateur ML déterministe destiné aux tests et au développement local."""

from app.application.ports.ml_service import AnomalyResult, ForecastResult, MLService
from app.domain.entities.sensor_reading import SensorReading


class MockMLAdapter(MLService):
    """Retourne des résultats configurables sans charger de modèles."""

    def __init__(
        self,
        predictions: list[float] | None = None,
        anomaly: AnomalyResult | None = None,
    ) -> None:
        self._predictions = predictions or [100.0, 110.0, 120.0]
        self._anomaly = anomaly or AnomalyResult(False, 0.0, "normal")

    @property
    def version(self) -> str:
        """Version fixe identifiant le faux service ML."""
        return "mock-1.0"

    async def forecast(self, machine_id: str, horizon_hours: int) -> ForecastResult:
        """Retourne les valeurs préparées et une enveloppe min/max."""
        if horizon_hours < 1 or horizon_hours > len(self._predictions):
            raise ValueError("Horizon demandé hors des prédictions configurées")
        values = self._predictions[:horizon_hours]
        return ForecastResult(values, min(values), max(values))

    async def detect_anomaly(self, readings: list[SensorReading]) -> AnomalyResult:
        """Retourne le diagnostic configuré pour les tests."""
        if not readings:
            raise ValueError("Au moins un relevé est nécessaire")
        return self._anomaly
