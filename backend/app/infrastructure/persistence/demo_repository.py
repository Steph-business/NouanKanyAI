"""Dépôts mémoire alimentés par les données de démonstration du projet."""

from datetime import UTC, datetime

from app.domain.entities.machine import Machine
from app.domain.entities.sensor_reading import SensorReading
from app.domain.repositories.machine_repository import MachineRepository
from app.domain.repositories.reading_repository import ReadingRepository
from app.domain.value_objects.machine_id import MachineId
from app.services.demo_data import load_demo_machine_state


class DemoMachineRepository(MachineRepository):
    """Adapte l'état démo existant au dépôt métier des machines."""

    async def get_by_id(self, machine_id: MachineId) -> Machine | None:
        """Recherche une machine dans les données démo locales."""
        return next((item for item in await self.list_all(False) if item.id == machine_id), None)

    async def list_all(self, active_only: bool = True) -> list[Machine]:
        """Convertit les lignes de démonstration en entités domaine."""
        machines = [
            Machine(
                id=MachineId(str(row["machine_id"])),
                name=str(row.get("nom", row["machine_id"])),
                location=str(row.get("site_nom", "Site de démonstration")),
                max_power_kw=max(float(row.get("power_kw", 1.0)) * 2, 1.0),
                is_active=str(row.get("status", "actif")).lower() in {"actif", "eco"},
            )
            for row in load_demo_machine_state()
        ]
        return [machine for machine in machines if machine.is_active] if active_only else machines

    async def save(self, machine: Machine) -> None:
        """Le dépôt démo est en lecture seule afin de ne pas simuler une persistance trompeuse."""
        raise NotImplementedError("Le dépôt de démonstration est en lecture seule")


class DemoReadingRepository(ReadingRepository):
    """Adapte les dernières mesures du jeu de démo au dépôt des capteurs."""

    async def list_for_machine(
        self, machine_id: MachineId, start: datetime | None = None, end: datetime | None = None
    ) -> list[SensorReading]:
        """Retourne un relevé récent si la machine est présente dans le jeu démo."""
        row = next(
            (
                item
                for item in load_demo_machine_state()
                if item.get("machine_id") == str(machine_id)
            ),
            None,
        )
        if row is None:
            return []
        timestamp = datetime.now(UTC)
        if start and timestamp < start:
            return []
        if end and timestamp > end:
            return []
        return [
            SensorReading(
                machine_id=machine_id,
                recorded_at=timestamp,
                power_kw=float(row.get("power_kw", 0.0)),
                temperature_c=float(row.get("temperature_c", 25.0)),
                vibration_hz=float(row.get("vibration_hz", 0.0)),
                pressure_bar=float(row.get("pressure_bar", 0.0)),
            )
        ]

    async def save(self, reading: SensorReading) -> None:
        """Le dépôt démo ne conserve pas les nouvelles mesures."""
        raise NotImplementedError("Le dépôt de démonstration est en lecture seule")
