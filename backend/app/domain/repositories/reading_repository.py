"""Contrat de persistance des relevés de capteurs."""

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.sensor_reading import SensorReading
from app.domain.value_objects.machine_id import MachineId


class ReadingRepository(ABC):
    """Interface asynchrone de lecture et sauvegarde des mesures."""

    @abstractmethod
    async def list_for_machine(
        self,
        machine_id: MachineId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[SensorReading]:
        """Retourne les relevés d'une machine dans une plage optionnelle."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, reading: SensorReading) -> None:
        """Persiste un nouveau relevé capteur."""
        raise NotImplementedError
