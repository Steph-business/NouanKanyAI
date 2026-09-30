"""Contrat de persistance des machines, sans choix de base de données."""

from abc import ABC, abstractmethod

from app.domain.entities.machine import Machine
from app.domain.value_objects.machine_id import MachineId


class MachineRepository(ABC):
    """Interface asynchrone de lecture et sauvegarde des machines."""

    @abstractmethod
    async def get_by_id(self, machine_id: MachineId) -> Machine | None:
        """Recherche une machine par son identifiant métier."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, active_only: bool = True) -> list[Machine]:
        """Retourne les machines, actives uniquement par défaut."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, machine: Machine) -> None:
        """Crée ou met à jour une machine."""
        raise NotImplementedError
