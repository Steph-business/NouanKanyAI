"""Adaptateur XGBoost réutilisant le ModelManager existant."""

import asyncio
from typing import Any

from app.application.ports.ml_service import ForecastResult
from app.domain.repositories.reading_repository import ReadingRepository
from app.domain.value_objects.machine_id import MachineId
from app.ml.manager import ModelManager


class XGBoostAdapter:
    """Enveloppe le prédicteur existant sans modifier ses algorithmes."""

    def __init__(self, model_manager: ModelManager, readings: ReadingRepository) -> None:
        self.model_manager = model_manager
        self.readings = readings

    @property
    def version(self) -> str:
        """Retourne la version chargée dans le registre du gestionnaire ML."""
        return self.model_manager.registry.get_latest_version()

    async def forecast(self, machine_id: str, horizon_hours: int) -> ForecastResult:
        """Exécute le modèle existant heure par heure à partir du dernier relevé."""
        observations = await self.readings.list_for_machine(MachineId(machine_id))
        if not observations:
            raise ValueError("Une mesure récente est requise pour lancer la prévision")
        latest = observations[-1]
        history: list[dict[str, Any]] = [
            {
                "power_kw": item.power_kw,
                "temperature_c": item.temperature_c,
                "timestamp": item.recorded_at.isoformat(),
            }
            for item in observations[-24:]
        ]
        predictions: list[float] = []
        current_power = latest.power_kw
        for _ in range(horizon_hours):
            result = await asyncio.to_thread(
                self.model_manager.predict,
                input_data={"power_kw": current_power, "temperature_c": latest.temperature_c},
                history=history,
            )
            current_power = float(result.predicted_value)
            predictions.append(current_power)
            history.append({"power_kw": current_power, "temperature_c": latest.temperature_c})
        # Le modèle historique ne fournit pas d'intervalle statistique; les bornes décrivent
        # l'étendue des valeurs prévues et ne doivent pas être interprétées comme IC calibré.
        return ForecastResult(predictions, min(predictions), max(predictions))
