"""Dépôt Supabase traduisant les lignes de la table machines en entités."""

import asyncio
from datetime import datetime
from typing import Any

from supabase import Client

from app.domain.entities.machine import Machine
from app.domain.repositories.machine_repository import MachineRepository
from app.domain.value_objects.machine_id import MachineId


class SupabaseMachineRepository(MachineRepository):
    """Implémente le dépôt machine sur la table Supabase `machines`."""

    def __init__(self, client: Client) -> None:
        self.client = client

    async def get_by_id(self, machine_id: MachineId) -> Machine | None:
        """Charge une ligne par code métier, puis par identifiant technique."""
        return await asyncio.to_thread(self._get_by_id_sync, machine_id)

    def _get_by_id_sync(self, machine_id: MachineId) -> Machine | None:
        response = (
            self.client.table("machines")
            .select("*")
            .eq("code_interne", str(machine_id))
            .limit(1)
            .execute()
        )
        rows: list[dict[str, Any]] = [dict(row) for row in response.data or []]
        if not rows:
            response = (
                self.client.table("machines")
                .select("*")
                .eq("id", str(machine_id))
                .limit(1)
                .execute()
            )
            rows = [dict(row) for row in response.data or []]
        return self._to_entity(rows[0]) if rows else None

    async def list_all(self, active_only: bool = True) -> list[Machine]:
        """Retourne les machines, filtrées sur les états actifs si demandé."""
        return await asyncio.to_thread(self._list_all_sync, active_only)

    def _list_all_sync(self, active_only: bool) -> list[Machine]:
        response = self.client.table("machines").select("*").execute()
        rows: list[dict[str, Any]] = [dict(row) for row in response.data or []]
        machines = [self._to_entity(row) for row in rows]
        return [machine for machine in machines if machine.is_active] if active_only else machines

    async def save(self, machine: Machine) -> None:
        """Enregistre une machine avec les colonnes du schéma métier existant."""
        await asyncio.to_thread(self._save_sync, machine)

    def _save_sync(self, machine: Machine) -> None:
        self.client.table("machines").upsert(
            {
                "code_interne": str(machine.id),
                "nom": machine.name,
                "emplacement": machine.location,
                "puissance_nominale_kw": machine.max_power_kw,
                "status": "actif" if machine.is_active else "inactif",
                "created_at": machine.created_at.isoformat()
                if machine.created_at
                else datetime.now().isoformat(),
            },
            on_conflict="code_interne",
        ).execute()

    @staticmethod
    def _to_entity(row: dict[str, Any]) -> Machine:
        """Convertit une ligne SDK (frontière dynamique) vers l'entité domaine."""
        machine_id = row.get("code_interne") or row.get("id")
        return Machine(
            id=MachineId(str(machine_id)),
            name=str(row.get("nom") or row.get("name") or machine_id),
            location=str(
                row.get("emplacement")
                or row.get("location")
                or row.get("site_id")
                or "Non associée"
            ),
            max_power_kw=float(row.get("puissance_nominale_kw") or row.get("max_power_kw") or 1.0),
            is_active=str(row.get("status", "actif")).lower()
            in {"actif", "active", "eco", "running"},
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            if row.get("created_at")
            else None,
        )
