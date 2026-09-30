"""Adaptateur Isolation Forest pour l'interface applicative ML."""

import asyncio

from app.application.ports.ml_service import AnomalyResult
from app.domain.entities.sensor_reading import SensorReading
from app.ml.manager import ModelManager


class IsolationForestAdapter:
    """Traduit un relevé multicapteur vers le détecteur existant."""

    def __init__(self, model_manager: ModelManager) -> None:
        self.model_manager = model_manager

    @property
    def version(self) -> str:
        """Retourne la version ML actuellement enregistrée."""
        return self.model_manager.registry.get_latest_version()

    async def detect_anomaly(self, readings: list[SensorReading]) -> AnomalyResult:
        """Analyse la mesure la plus récente avec les caractéristiques attendues."""
        if not readings:
            raise ValueError("Au moins un relevé est nécessaire")
        current = readings[-1]
        previous_power = readings[-2].power_kw if len(readings) > 1 else None
        delta = current.power_kw - previous_power if previous_power is not None else 0.0
        result = await asyncio.to_thread(
            self.model_manager.detect_anomaly,
            input_data={
                "power_kw": current.power_kw,
                "temperature_c": current.temperature_c,
                "vibration_hz": current.vibration_hz,
                "pressure_bar": current.pressure_bar,
                "power_rolling_std": 0.0,
                "consumption_delta": delta,
                "hour": current.recorded_at.hour,
            },
            previous_power=previous_power,
        )
        return AnomalyResult(
            is_anomaly=result.is_anomaly,
            score=result.score,
            severity=result.severity,
        )
