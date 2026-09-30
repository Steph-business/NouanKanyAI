"""Dépôt Supabase traduisant sensor_metrics en relevés domaine."""

import asyncio
from datetime import datetime
from typing import Any

from supabase import Client

from app.domain.entities.sensor_reading import SensorReading
from app.domain.repositories.reading_repository import ReadingRepository
from app.domain.value_objects.machine_id import MachineId


class SupabaseReadingRepository(ReadingRepository):
    """Implémente le dépôt des mesures sur `sensor_metrics`."""

    def __init__(self, client: Client) -> None:
        self.client = client

    async def list_for_machine(
        self, machine_id: MachineId, start: datetime | None = None, end: datetime | None = None
    ) -> list[SensorReading]:
        """Lit chronologiquement les relevés associés au code machine demandé."""
        return await asyncio.to_thread(self._list_for_machine_sync, machine_id, start, end)

    def _list_for_machine_sync(
        self, machine_id: MachineId, start: datetime | None, end: datetime | None
    ) -> list[SensorReading]:
        machine = SupabaseMachineLookup(self.client)._get_database_id_sync(machine_id)
        query = self.client.table("sensor_metrics").select("*").eq("machine_id", machine)
        if start is not None:
            query = query.gte("recorded_at", start.isoformat())
        if end is not None:
            query = query.lte("recorded_at", end.isoformat())
        response = query.order("recorded_at").execute()
        rows: list[dict[str, Any]] = [dict(row) for row in response.data or []]
        return [self._to_entity(row, machine_id) for row in rows]

    async def save(self, reading: SensorReading) -> None:
        """Ajoute une mesure liée à l'identifiant technique Supabase de la machine."""
        await asyncio.to_thread(self._save_sync, reading)

    def _save_sync(self, reading: SensorReading) -> None:
        database_id = SupabaseMachineLookup(self.client)._get_database_id_sync(reading.machine_id)
        self.client.table("sensor_metrics").insert(
            {
                "machine_id": database_id,
                "recorded_at": reading.recorded_at.isoformat(),
                "power_kw": reading.power_kw,
                "temperature_c": reading.temperature_c,
                "vibration_hz": reading.vibration_hz,
                "pressure_bar": reading.pressure_bar,
            }
        ).execute()

    @staticmethod
    def _to_entity(row: dict[str, Any], machine_id: MachineId) -> SensorReading:
        """Convertit une ligne capteur en objet immuable du domaine."""
        timestamp = datetime.fromisoformat(str(row["recorded_at"]).replace("Z", "+00:00"))
        return SensorReading(
            machine_id=machine_id,
            recorded_at=timestamp,
            power_kw=float(row["power_kw"]),
            temperature_c=float(row.get("temperature_c", 25.0)),
            vibration_hz=float(row.get("vibration_hz", 0.0)),
            pressure_bar=float(row.get("pressure_bar", 0.0)),
        )


class SupabaseMachineLookup:
    """Résout le code machine métier vers sa clé étrangère Supabase."""

    def __init__(self, client: Client) -> None:
        self.client = client

    async def get_database_id(self, machine_id: MachineId) -> str:
        """Retourne l'identifiant technique de la machine ou signale son absence."""
        return await asyncio.to_thread(self._get_database_id_sync, machine_id)

    def _get_database_id_sync(self, machine_id: MachineId) -> str:
        response = (
            self.client.table("machines")
            .select("id")
            .eq("code_interne", str(machine_id))
            .limit(1)
            .execute()
        )
        rows: list[dict[str, Any]] = [dict(row) for row in response.data or []]
        if not rows:
            raise ValueError(f"Machine inconnue: {machine_id}")
        return str(rows[0]["id"])
